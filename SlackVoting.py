import SimpleCMDVote
import time
import os
import sys
import queue
import threading
import SlackCred
import json
from slackclient import SlackClient

#Load template data
template = None
try:
    with open(sys.argv[1]) as templateFile:
        template = json.load(templateFile)
except IndexError:
    print('Usage: SlackVoting.py <templateFile>')
    exit(1)

#Connect to slack
sc = SlackClient(os.environ.get(['VOTING_BOT_TOKEN']))
assert(sc.rtm_connect())

#Find the bot's user ID
userList = sc.api_call(
    'users.list')['members']
ID = filter(lambda x: x['name']=='votebot', userList).__next__()['id']

#Queue containing messages to be posted, in the format (channel,text)
#Locked by messageQueueLock
messageQueueLock = threading.Lock()
messageQueue = queue.Queue()

#Class that concurrently handles the different conversations
class ConversationThread(threading.Thread):
    channel = None
    def __init__(self, channel):
        #Run super-constructor
        threading.Thread.__init__(self)
        self.channel = channel

    def postMessage(self, message):
        messageQueueLock.acquire(1)
        messageQueue.put((self.channel,message))
        messageQueueLock.release()

    def getInput(self, prompt):
        self.postMessage(prompt)
        shouldRead = False
        while not shouldRead:
            shouldRead = not queues[self.channel].empty()
            time.sleep(1)
        userInput = queues[self.channel].get()
        return userInput['text']

    def run(self):
        vote = SimpleCMDVote.CMDVotingSystem(self.getInput, self.postMessage, template)
        vote.simpleCMD()
        #Clean up
        alreadyVoted.append(self.channel)


class ManagementConsole(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)



generalChannelId = 'C0DJMPU7L'
#Connect to the general channel, post a message, then leave
def makeAnnoucement(message):
    sc.api_call('channels.join', name=generalChannelId)
    sc.api_call('chat.postMessage', channel=generalChannelId, text=message)
    sc.api_call('channels.leave', name=generalChannelId)


#Dict w/ channel:thread
threadManager = {}
threadManagerLock = threading.Lock()
#Dict of ques w/ channel:queue, locked by queueLock
queues = {}
queueLock = threading.Lock()
#List of channels that have already voted
alreadyVoted = []

#Message reading loop
makeAnnoucement('Vote open, pm me to fill out a ballot')
while True:
    #Read from the firehouse
    for message in filter(lambda x: (x['type'] == 'message') and ('user' in x) and (x['channel'] not in alreadyVoted), sc.rtm_read()):
        if message['channel'] not in threadManager:
            #We need to create a new thread to manage this conversation
            thread = ConversationThread(message['channel'])
            threadManager[message['channel']] = thread
            #Init the inter-thread dictionaries
            queues[message['channel']] = queue.Queue()
            thread.start()
        else:
            #Add message to that channels queue
            queues[message['channel']].put(message)
    time.sleep(1)
    #Post queued messages
    messageQueueLock.acquire(1)
    while not messageQueue.empty():
        next = messageQueue.get()
        sc.api_call('chat.postMessage', channel=next[0], text=next[1])
    messageQueueLock.release()
    time.sleep(1)





