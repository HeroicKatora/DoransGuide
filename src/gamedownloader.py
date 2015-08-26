'''
Created on 25.08.2015

@author: Katora
'''

from itertools import product, zip_longest
from collections import defaultdict
from multiprocessing.pool import ThreadPool
import json
import pickle
import traceback
import time
import optparse
import copy
from matchinfo import loadGame, item_events
from lolstatic import relevantVersions
from riotapi import AnswerException

class MatchDownloader():
    def __init__(self):
        self.gamesdone = defaultdict(set)
        self.datasets = []
        self.failedset = defaultdict(set)
        self.gamesToDo = 0
        
        self.progress_file = '../data/raw/workedData.pkl'
        try:                                                    #Restore progress we made in previous sessions
            with open(self.progress_file, 'br') as progress_fh:
                self.gamesdone = pickle.load(progress_fh)
                self.datasets = pickle.load(progress_fh)
                self.failedset = pickle.load(progress_fh)
        except:
            pass
    
    
    def printCompletion(self):
        print("Done: ", sum(len(self.gamesdone[a]) for a in self.gamesdone), " of ~", self.gamesToDo, " games to analyze.")
        print("Failed: ", sum(len(self.failedset[a]) for a in self.failedset), "Number of data sets: ", len(self.datasets))
        print("Detailed fail statistics: ", {x:len(self.failedset[x]) for x in self.failedset})
        
    def download(self, gametuple):
        gameId, region = gametuple
        region = region.lower()
        if gameId in self.gamesdone[region] or (gameId in self.failedset[region] and self.ignoreFailedFiles):         #Skip games that are already loaded
            return
        
        try:
            gameLog = loadGame(region, gameId)
            gameData = item_events(gameLog)
        except AnswerException as e:
            if e.answer.status not in [403, 404, 429, 503, 719]:      #Certain server statuses are not to be considered a definitive failure for the download routine
                raise
            print(e)
            if e.answer.status in [403, 404, 503]:
                self.failedset[region].add(gameId)
            return
        self.datasets.extend(gameData)                           #If everything worked out, add the game and mark it as done
        self.gamesdone[region].add(gameId)
    
    
    def work(self):
        gamelists = []
        for patch in relevantVersions:                          # Construct a list of tuples, each containing a game id and a region
            patch = patch[0:4]
            for queue in ['NORMAL_5X5', 'RANKED_SOLO']:
                for region in ['BR', 'EUNE', 'LAN', 'LAS', 'NA', 'OCE']: # 'EUW', 'KR', 'RU', 'TR',
                    with open("../itemsets/{patch}/{queue}/{region}.json".format(**locals())) as filehandle:
                        games = json.load(filehandle)
                        self.gamesToDo += len(games)
                        gamelists.append(product(games, [copy.copy(region)]))
        self.printCompletion()
        
        try:
            with ThreadPool(8) as dl_pool:            #Round robin through the different categories to get a good coverage of all possible combinations
                dl_pool.map_async(self.download, (game_reg for games in zip_longest(*gamelists) for game_reg in games if game_reg is not None))
                _ = input()
                dl_pool.terminate()
        except Exception:
            traceback.print_exc()
        finally:
            with open(self.progress_file, 'bw') as progress_fh:              #At the end, dump the progress of the downloader no matter what caused it to stop
                pickle.dump(self.gamesdone, progress_fh)
                pickle.dump(self.datasets, progress_fh)
                pickle.dump(self.failedset, progress_fh)
            with open("{0}.{1}".format(self.progress_file,time.time()), 'bw') as progress_fh:    #Create a backup file for every snapshot
                pickle.dump(self.gamesdone, progress_fh)
                pickle.dump(self.datasets, progress_fh)
                pickle.dump(self.failedset, progress_fh)
        
        self.printCompletion()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-f", "--failed", action="store_false", dest="ignoreFailedFiles",
                      default=True, help="Retry previously failed game ids")
    parser.add_option("-k", default = False, action="store", dest="key", type="string", help="Retry previously failed game ids")
    matchDownloader = MatchDownloader()
    matchDownloader.ignoreFailedFiles = parser.parse_args()[0].ignoreFailedFiles
    matchDownloader.work()
 
