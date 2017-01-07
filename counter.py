import json, os, sys
from typing import List

def _ballotsToList(directory) -> List:
    data = []
    print(directory)
    print(os.listdir(directory))
    #Grab all the files that end in .json
    for filename in filter(lambda x: x[-5:]=='.json', os.listdir(directory)):
        filepath = "./ballots/" + filename
        with open(filepath) as json_data:
            d = json.load(json_data)
            try:
                data.append(d["ranked"])
            except KeyError:
                print('Error parsing ballot: ' + filename + ' Key not found')
    return data

def _tallyRanking(ballots, numOfOptions, optionsEliminated = []) -> List:
    choice = _tallyRunoff(ballots, optionsEliminated)
    rankingList = []
    rankingList.append(choice)
    optionsEliminated.append(choice)
    if len(optionsEliminated) == numOfOptions:
        return rankingList
    else:
        return rankingList + _tallyRanking(ballots, numOfOptions, optionsEliminated)

def _tallyRunoff(ballots: List, optionsEliminated = []):
    #returns string
    dic = {}
    # count top votes
    for ballot in ballots:
        choice = _topChoice(ballot, optionsEliminated)
        if choice not in dic:
            dic[choice] = 1
        else:
            dic[choice] += 1
    #see if any vote has a majority
    for option in dic:
        if dic[option] > len(ballots)/2:
            return option
    lowestChoice = None
    lowestValue = float('inf')
    for option in dic:
        if dic[option] < lowestValue:
            lowestValue = dic[option]
            lowestChoice = option
    optionsEliminated.append(lowestChoice)
    #clean out empty ballots to ensure someone can eventually get a majority
    for ballot in ballots:
        shouldRemove = True
        for choice in ballot:
            if choice not in optionsEliminated:
                shouldRemove = False
        if shouldRemove:
            ballots.remove(ballot)
    return _tallyRunoff(ballots, optionsEliminated)

def _topChoice(ballot, optionsEliminated = []):
    highestRank = float('inf')
    bestOption = None
    for option in ballot:
        if option not in optionsEliminated:
            if ballot[option] < highestRank:
                highestRank = ballot[option]
                bestOption = option
    return bestOption

def _getNumOfOptions(ballots):
    options = []
    for ballot in ballots:
        for option in ballot:
            if option not in options:
                options.append(option)
    return len(options)

def countBallots(folder):
    ballots = _ballotsToList(folder)
    return _tallyRanking(ballots, _getNumOfOptions(ballots))


if __name__ == '__main__':
    path = './ballots/'
    try:
        path = sys.argv[1]
    except IndexError:
        print('Assuming default path of ./ballots/')
    results = countBallots(path)
    print('Results: \n')
    print(results)

