import os
import sys
import json
import maya
from random import shuffle


class CMDVotingSystem:

    #Fields
    inputM = None
    outputM = None
    template = None

    __numberMapping = {
        1:'First',
        2:'Second',
        3:'Third',
        4:'Fourth',
        5:'Fifth',
        6:'Sixth'
    }

    __commands = ['List', 'Reset', 'Seal']


    def __init__(self, inputM, outputM, template):
        self.inputM = inputM
        self.outputM = outputM
        self.template = template


    def __printOptions(self, options):
        return 'Voting options include:\n' + '\n'.join(map(lambda x: '\t' + x, options))


    def __sealBallot(self, ballotData):
        message = 'Your ballot currently reads\n'
        message += '\n'.join(map(lambda x: str(x+1) + ': ' + ballotData[x], range(len(ballotData))))
        self.outputM(message)
        ans = self.inputM('Are you sure you want to seal? (y/n) ')
        if ans not in ['yes', 'y', 'Y']:
            return False
        ranked = {'ranked':ballotData}
        filename = maya.now().iso8601().replace('.','').replace(':','') + '.json'
        with open(filename, 'w') as ballot:
            ballot.write(json.dumps(ranked))
            return True

    def simpleCMD(self):
        #Map the template to use standard capitalization
        self.template['options'] = list(map(lambda x: x.capitalize(), self.template['options']))
        startMessage = 'Welcome to the simple CMD Vote! \n' + \
            'Commands include: \n' + \
            '\t list: lists all the possible options\n' + \
            '\t reset: reset your ballot\n' + \
            '\t seal: seals & finished your ballot\n' + \
            '\t Vote by typing option,option,option\n' + \
            '\t Ex: ' + (','.join(self.template['options']))
        startMessage += self.__printOptions(self.template['options'])
        self.outputM(startMessage)
        pos = 1
        finished = False
        submitted = False
        options = []
        while not finished:
            if pos > len(self.template['options']) or submitted:
                    finished = self.__sealBallot(options)
                    if not finished:
                        options = []
                        submitted = False
                        pos = 1
                        self.outputM('Ballot reset to empty')
            else:
                cmd = self.inputM(self.__numberMapping[pos] + ' choice: ').capitalize()
                if cmd in self.template['options']:
                    options.append(cmd)
                    pos += 1
                elif ',' in cmd:
                    #Break the ballot apart
                    choices = cmd.split(',')
                    if all(map(lambda x: x.capitalize() in self.template['options'], choices)):
                        options = choices
                        submitted = True
                elif cmd in self.__commands:
                    if cmd == 'List':
                        self.__printOptions(self.template['options'])
                    elif cmd == 'Reset':
                        self.outputM('Ballot reset to empty')
                        pos = 1
                        options = []
                        submitted = False
                    elif cmd == 'Seal':
                        finished = self.__sealBallot(options)
                else:
                     self.outputM('Bad option! Sorry!')
        self.outputM('Thanks, your ballot has been saved!')


if __name__ == '__main__':
    #Read template from file
    try:
        with open(sys.argv[1]) as template:
            templateData = json.load(template)
    except IndexError:
        print('Usage: SimpleCMDVote.py <templateFile>')
        exit(1)
    vote = CMDVotingSystem(input, print, templateData)
    vote.simpleCMD()
