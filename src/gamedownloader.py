'''
Created on 25.08.2015

@author: Katora
'''

from matchinfo import loadGame, item_events
from lolstatic import relevantVersions
from itertools import product, zip_longest
import json
import pickle
import traceback
from riotapi import AnswerException
import time
import optparse
from collections import defaultdict

if __name__ == '__main__':
    progress_file = '../data/raw/workedData.pkl'
    
    parser = optparse.OptionParser()
    parser.add_option("-f", "--failed", action="store_false", dest="ignoreFailedFiles",
                      default=True, help="Retry previously failed game ids")
    ignoreFailedFiles = parser.parse_args()[0].ignoreFailedFiles
    
    gamesdone = defaultdict(set)
    datasets = []
    failedset = defaultdict(set)
    
    def printCompletion():
        print("Done: ", sum(len(gamesdone[a]) for a in gamesdone), " of ~", gamesToDo, " games to analyze.")
        print("Failed: ", sum(len(gamesdone[a]) for a in gamesdone), "Number of data sets: ", len(datasets))
        print("Detailed fail statistics: ", {x:len(failedset[x]) for x in failedset})
        
    try:                                                    #Restore progress we made in previous sessions
        with open(progress_file, 'br') as progress_fh:
            gamesdone = pickle.load(progress_fh)
            datasets = pickle.load(progress_fh)
            failedset = pickle.load(progress_fh)
    except:
        pass
    
    gamesToDo = 0
    gamelists = []
    for patch in relevantVersions:                          # Construct a list of tuples, each containing a game id and a region
        patch = patch[0:4]
        for queue in ['NORMAL_5X5', 'RANKED_SOLO']:
            for region in ['NA']:#[''' 'BR', 'EUNE', 'EUW', 'KR', 'LAN', 'LAS',''' 'NA', 'OCE', 'RU', 'TR']:
                with open("../itemsets/{patch}/{queue}/{region}.json".format(**locals())) as filehandle:
                    games = json.load(filehandle)
                    gamesToDo += len(games)
                    gamelists.append(product(games, [region]))
    printCompletion()
    try:
        for games in zip_longest(*gamelists):
            for game_reg in games:              #Round robin through the different categories to get a good coverage of all possible combinations
                if game_reg is None:
                    continue
                gameId, region = game_reg
                region = region.lower()
                if gameId in gamesdone[region] or (gameId in failedset[region] and ignoreFailedFiles):         #Skip games that are already loaded
                    continue
                
                try:
                    gameLog = loadGame(region, gameId)
                    gameData = item_events(gameLog)
                except AnswerException as e:
                    if e.answer.status not in [403, 404, 503]:      #Certain server statuses are not to be considered a definitive failure for the download routine
                        raise
                    print(e)
                    failedset[region].add(gameId)
                    continue
                datasets.append(gameData)                           #If everything worked out, add the game and mark it as done
                gamesdone[region].add(gameId)
    except Exception as e:
        traceback.print_exc()
    finally:
        with open(progress_file, 'bw') as progress_fh:              #At the end, dump the progress of the downloader no matter what caused it to stop
            pickle.dump(gamesdone, progress_fh)
            pickle.dump(datasets, progress_fh)
            pickle.dump(failedset, progress_fh)
        with open("{0}.{1}".format(progress_file,time.time()), 'bw') as progress_fh:    #Create a backup file for every snapshot
            pickle.dump(gamesdone, progress_fh)
            pickle.dump(datasets, progress_fh)
            pickle.dump(failedset, progress_fh)
    
    printCompletion()
