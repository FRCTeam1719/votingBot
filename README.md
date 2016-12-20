# votingBot
A Slack Bot for counting votes during kickoff

Admin:
The admin has the following powers:
 - set the options to vote on
 - count the vote
 - vote multiple times (so that the admin's phone/computer can be used as a voting booth for students without phones or accounts)

Setting the options:
To set the options, the admin dm's the bot 'set options: <op1>, <op2>,...'

Counting the vote:
To count the vote, the admin dm's the bot 'count'
The admin will be prompted with who has not voted yet. They should respond 'count anyway' to go ahead witht the vote
and 'cancel count' to wait until more people have voted. After the votes are counted, the results will be posted to #general

Voting:
To see the options to vote on, along with their corrisponding letter codes, the user messages the bot "show ballot"
To vote, the user messages the bot "vote: <choice1code>, <choice2code>,..." like "vote: b, c, d, a"
