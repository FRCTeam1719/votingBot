import time, key, counter, string
from slackclient import SlackClient
from user import user
from pprint import pprint

admin = 'elilitwack'
sc = SlackClient(key.API_KEY)
assert(sc.rtm_connect())
hasShownCountConfirmMessage = False
options = None

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
#temp list to grab names from
temp_userList = sc.api_call('users.list',)['members']
users = []
for u in temp_userList:
    dm = '@' + u['name']
    isAdmin = (dm == '@'+admin)
    users.append(user(dm, isAdmin, True))

for u in users:
    print(u)

def processMessage(i):
    global hasShownCountConfirmMessage, options
    body = i['text']
    body = body.lower()
    if body == 'count ballots' or body == 'count votes' or body == 'count':
        if resolveUser(i['user']) == admin and not hasShownCountConfirmMessage:
            message = "Are you sure you want to count the votes? The following users have not yet voted: "
            for u in users:
                if not u.hasVoted:
                    message = message + u.dm + ', '
            message = message + 'To cancel the vote, respond "cancel count", to go ahead, respond "count anyway"'
            postMessage(message, i['channel'])
            hasShownCountConfirmMessage = True
        elif resolveUser(i['user']) == admin and hasShownCountConfirmMessage:
            message = "Please confirm or cancel your previous request to count before creating a new one"
            postMessage(message, i['channel'])
        else:
            message = 'You are not athorized to request a vote count! Only ' + admin + ' can do that.'
            postMessage(message, i['channel'])
    elif body == 'cancel count':
        if resolveUser(i['user']) == admin
            if hasShownCountConfirmMessage:
                hasShownCountConfirmMessage = False
                message = "Okay, We'll wait a bit"
                postMessage(message, i['channel'])
            else:
                message = "Hold up there cowboy! You can't cancel your request to count if you haven't made one yet."
        else:
            message = "Woah there! Only " + admin + " can deal with counting the vote!"
    elif body == 'count anyway':
        if resolveUser(i['user']) == admin:
            if hasShownCountConfirmMessage:
                hasShownCountConfirmMessage = False
                message = "Okay, I'll count it up"
                postMessage(message, i['channel'])
                count = counter.countBallots()
                message = "Here's the votes, folks: " + count.__str__()
                postMessage(message, '#general')
            else:
                message = "Careful there! You can't confirm your request to count if you haven't made one yet."
        else:
            message = "Woah there! Only " + admin + " can deal with counting the vote!"
    elif body == 'help':
        message = 'To vote, type "vote" and follow the instructions.'
        postMessage(message, i['channel'])
    elif body == "show options":
        if options == None:
            message = "Sorry Friendo, the options haven't been set yet. Bug " + admin + "about it"
            postMessage(message, i['channel'])
        else:
            message = "Here are the options: "
            i = 0
            while i<len(options):
                if i != 0:
                    message += ', '
                message += '{' + options[i] + ": " + list(string.ascii_lowercase) +'}'
                i += 1
            postMessage(message, i['channel'])
    elif body[:5] == "vote:":
        #allow user to vote
        if options == None:
            message = "Sorry Comrade, the options haven't been set yet. Bug " + admin + "about it"
            postMessage(message, i['channel'])
        else:
            rawInput = body[5:]
    elif body[:12] == "set options:":
        #set options
        if resolveUser(i['user']) == admin:
            rawOptions = body[12:]
            options = rawOptions.split(',')
            #if the first or last character in each option is a space, remove it
            i = 0
            while i < len(options):
                if options[i][0] == ' ':
                    options[i] = options[i][1:]
                if options[i][-1] == ' ':
                    options[i] = options[i][:-1]
                i += 1
            message = "Okay, these are the options: " + options
        else:
            message = "Wait a minute, buster! Only " + admin + " can set the options to vote on."
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