import os
import sys
import json
import maya




numberMapping = {
    1:'First',
    2:'Second',
    3:'Third',
    4:'Fourth',
    5:'Fifth',
    6:'Sixth'
}

commands = ['List', 'Reset', 'Seal']

def readBallotTemplate(filename):
    with open(filename, 'r') as template:
        data = json.load(template)
    return data

def printOptions(options):
    print('Voting options include: ')
    for line in map(lambda x: '\t'+x, options):
        print(line)

def sealBallot(ballotData):
    print('Your ballot currently reads: ')
    for i in range(len(ballotData)):
        print(str(i+1) + ': ' + ballotData[i])
    ans = input('Are you sure you want to seal? (y/n) ')
    if ans not in ['yes', 'y', 'Y']:
        return False
    ranked = {'ranked':ballotData}
    filename = maya.now().iso8601().replace('.','').replace(':','') + '.json'
    with open(filename, 'w') as ballot:
        ballot.write(json.dumps(ranked))
        return True

if __name__ == '__main__':
    try:
        ballot = readBallotTemplate(sys.argv[1])
    except IndexError:
        print('Usage: simmpleCMDVote.py <ballotTemplate>')
        exit(1)
    #Map the ballot to use standard capitalization
    ballot['options'] = list(map(lambda x: x.capitalize(), ballot['options']))
    print('Welcome to the simple CMD vote!')
    print('Commands include: ')
    print('\t list: lists all the possible options')
    print('\t reset: reset your ballot')
    print('\t seal: seals & finishes your ballot')
    printOptions(ballot['options'])
    pos = 1
    finished = False
    options = []
    while not finished:
        if pos > len(ballot['options']):
            finished = sealBallot(options)
        else:
            cmd = input(numberMapping[pos] + ' choice: ').capitalize()
            if cmd in ballot['options']:
                options.append(cmd)
                pos += 1
            elif cmd in commands:
                if cmd == 'List':
                    printOptions(ballot['options'])
                elif cmd == 'Reset':
                    print('Ballot reset to empty')
                    pos = 1
                    options = []
                elif cmd == 'Seal':
                    finished = sealBallot(options)
            else:
                 print('Bad option! Sorry!')

