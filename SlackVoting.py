import SimpleCMDVote
import time
import os
import sys
import queue
import threading
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
sc = SlackClient(os.environ.get('VOTE_BOT_TOKEN'))
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

    def stop(self):
        self.vote.finished = True
        self.postMessage('Sorry, voting is over')

    def run(self):
        self.vote = SimpleCMDVote.CMDVotingSystem(self.getInput, self.postMessage, template)
        self.vote.simpleCMD()
        #Clean up
        alreadyVoted.append(self.channel)



generalChannelId = 'C0DJMPU7L'
#Connect to the general channel, post a message, then leave


#Dict w/ channel:thread
threadManager = {}
threadManagerLock = threading.Lock()
#Dict of ques w/ channel:queue, locked by queueLock
queues = {}
queueLock = threading.Lock()
#List of channels that have already voted
alreadyVoted = []
shouldRun = True

class Manager(threading.Thread):
    running = None
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def stop(self):
        self.running = False

    def makeAnnoucement(self, message):
        sc.api_call('channels.join', name=generalChannelId)
        sc.api_call('chat.postMessage', channel=generalChannelId, text=message)
        sc.api_call('channels.leave', name=generalChannelId)

    def run(self):
        #Message reading loop
        # self.makeAnnoucement('Vote open, pm me to fill out a ballot')
        while self.running:
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
                if next[0] == 'GENERAL':
                    self.makeAnnoucement(next[1])
                else:
                    sc.api_call('chat.postMessage', channel=next[0], text=next[1])
            messageQueueLock.release()
            time.sleep(1)



print('INIT REACHED')
threadManagerLock.acquire(1)
threadManager['MANAGER'] = Manager()
threadManager['MANAGER'].start()
threadManagerLock.release()
print('Created manager')
while shouldRun:
    print('Management console active\n')
    #Create management console
    cmd = input('> ')
    if 'announce' in cmd:
        message = cmd[cmd.index('"'):cmd[::-1].index('"')]
        messageQueueLock.acquire(1)
        messageQueue.put(('GENERAL',message))
        messageQueueLock.release()
    elif cmd == 'stop':
        threadManagerLock.acquire(1)
        conversations = map(lambda x: x[1], filter(lambda x: x[0]!='GENERAL', threadManager.items()))
        manager = threadManager['MANAGER']
        threadManagerLock.release()
        for i in conversations:
            i.stop()
        manager.stop()
        manager.join()
        shouldRun = False
    else:
        print('Bad Command')
print('Exiting')
exit(0)
