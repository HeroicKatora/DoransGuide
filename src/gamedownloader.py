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
import shutil
import os
from threading import Lock
from matchinfo import loadGame, item_events
from lolstatic import relevantVersions
from riotapi import AnswerException

downloadPath = '../data/raw'

class MatchDownloader(object):
    def __init__(self, ignoreFailed):
        self.gamesdone = defaultdict(set)
        self.datasets = []
        self.failedset = defaultdict(set)
        self.gamesToDo = 0
        
        if not os.path.exists(downloadPath):
            os.makedirs(downloadPath)
        self.progress_file = os.path.join(downloadPath, 'done.pkl')
        self.failed_file   = os.path.join(downloadPath, 'failed.pkl')
        self.data_file     = os.path.join(downloadPath, 'data_{time}.pkl')
        self.threshhold = 10**6      #Number of data sets that lie in memory at the same time
        
        self.ignoreFailedFiles = ignoreFailed
        try:                                                    #Restore progress we made in previous sessions
            with open(self.progress_file, 'br') as progress_fh:
                self.gamesdone = pickle.load(progress_fh)
        except:
            pass
        try:
            with open(self.failed_file, 'br') as failed_fh:
                self.failedset = pickle.load(failed_fh)
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
            print(e)
            if e.answer.status not in [403, 404, 429, 503, 719]:      #Certain server statuses are not to be considered a definitive failure for the download routine
                raise
            if e.answer.status in [403, 404, 503]:
                self.failedset[region].add(gameId)
            return
        self.datasets.extend(gameData)                           #If everything worked out, add the game and mark it as done
        self.gamesdone[region].add(gameId)
    
    
    def work(self):
        gamelists = []
        for patch in relevantVersions:                    # Construct a list of tuples, each containing a game id and a region
            patch = patch[0:4]
            for queue in ['NORMAL_5X5', 'RANKED_SOLO']: 
                for region in ['EUW', 'KR', 'RU', 'TR', 'BR', 'EUNE', 'LAN', 'LAS', 'NA', 'OCE']: #[]:
                    with open("../itemsets/{patch}/{queue}/{region}.json".format(**locals())) as filehandle:
                        games = json.load(filehandle)
                        self.gamesToDo += len(games)
                        gamelists.append(product(games, [copy.copy(region)]))
        self.printCompletion()
        
        callbacklock = Lock()
        def dataSafeCallback(result):
            if len(self.datasets) > self.threshhold:
                if not callbacklock.acquire(blocking = False):
                    return
                self.safePartial()
                callbacklock.release()
                    
        try:
            with ThreadPool(16) as dl_pool:            #Round robin through the different categories to get a good coverage of all possible combinations
                print("Cancel by pressing Return")
                def make_noise(exception):
                    print("A worker failed: ", exception)
                    return
                
                for gametuple in (game_reg for games in zip_longest(*gamelists) for game_reg in games if game_reg is not None):
                    dl_pool.apply_async(self.download, (gametuple,), callback = dataSafeCallback, error_callback = make_noise)
                _ = input()
                dl_pool.terminate()
        except Exception:
            traceback.print_exc()
        finally:
            now = time.time()
            with open(self.progress_file, 'bw') as progress_fh:              #At the end, dump the progress of the downloader no matter what caused it to stop
                pickle.dump(self.gamesdone, progress_fh)
            shutil.copyfile(self.progress_file, "{0}.{1}".format(self.progress_file,time.time()))
            with open(self.failed_file, 'bw') as failed_fh:
                pickle.dump(self.failedset, failed_fh)
            shutil.copyfile(self.failed_file, "{0}.{1}".format(self.failed_file,time.time()))
            with open(self.data_file.format(time = now), 'bw') as data_fh:
                pickle.dump(self.datasets, data_fh)
        
        self.printCompletion()
        
    def safePartial(self):
        dataCopy = self.datasets[:]
        with open(self.data_file.format(time = time.time()), 'bw') as data_fh:
            pickle.dump(dataCopy, data_fh)
        self.datasets[:len(dataCopy)] = []

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-f", "--failed", action="store_false", dest="ignoreFailedFiles",
                      default=True, help="Retry previously failed game ids")
    parser.add_option("-k", default = False, action="store", dest="key", type="string", help="Retry previously failed game ids")
    options, args = parser.parse_args()
    matchDownloader = MatchDownloader(options.ignoreFailedFiles)
    matchDownloader.work()
 
