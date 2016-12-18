import time
import os
from slackclient import SlackClient

sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
assert(sc.rtm_connect())

sc.api_call(
    'channels.join',
    channel='C3D941E2G'
)


def postMessage(text, channel):
    sc.api_call('chat.postMessage',
                channel=channel,
                text=text)


#Resolves a userID to a clean username
def resolveUser(userID):
    userList = sc.api_call('users.list')['members']
    name = filter(lambda x: x['id']==userID, userList).__next__()['real_name']
    return name


#Get bot ID
userList = sc.api_call(
    'users.list',
    )['members']
ID = filter(lambda x: x['name']=='ideabot', userList).__next__()['id']
admins = ['aaroneline']
adminIDs = list(map(lambda x: x['id'], filter(lambda x: x['name'] in admins, userList)))


def processMessage(i):
    if i['text'] == 'help':
        helpMessage = 'Send me an idea in the format: "idea: <you\'re idea>" and I\'ll post it for you in #ideas!'
        postMessage(helpMessage, i['channel'])
    elif i['text'][:5] == 'idea:':
        response = 'Thanks, forwarding this for you!'
        postMessage(response, i['channel'])
        index = None
        if i['text'][6] == ' ':
            index = 6
        else:
            index = 5
        message = resolveUser(i['user']) + " says: " + i['text'][index:]
        postMessage(message, '#ideas')
    else:
        unknown = "Sorry! I don't understand! Try 'help' for help!"
        postMessage(unknown, i['channel'])



while(True):
    messages = sc.rtm_read()
    #Process messages
    for i in messages:
        shouldProcess = False
        try:
            if i['type'] == 'message' and i['user'] != ID:
                shouldProcess = True
        except(KeyError):
            if i['type'] == 'message' and i['bot_id']==ID:
                shouldProcess = True
        if shouldProcess:
            processMessage(i)
time.sleep(1)