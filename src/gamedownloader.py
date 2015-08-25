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

if __name__ == '__main__':
    progress_file = '../data/raw/workedData.pkl'
    
    gamesdone = set()
    datasets = []
    try:
        with open(progress_file, 'br') as progress_fh:
            gamesdone = pickle.load(progress_fh)
            datasets = pickle.load(progress_fh)
    except:
        pass
    
    gamelists = []
    for patch in relevantVersions:
        patch = patch[0:4]
        for queue in ['NORMAL_5X5', 'RANKED_SOLO']:
            for region in ['BR', 'EUNE', 'EUW', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'RU', 'TR']:
                with open("../itemsets/{patch}/{queue}/{region}.json".format(**locals())) as filehandle:
                    games = json.load(filehandle)
                    gamelists.append(product(games, [region]))
    
    try:
        for games in zip_longest(*gamelists):
            for game_reg in games:
                if game_reg is None:
                    continue
                gameId, region = game_reg
                region = region.lower()
                if gameId in gamesdone:
                    continue
                
                try:
                    gameLog = loadGame(region, gameId)
                    gameData = item_events(gameLog)
                except AnswerException as e:
                    if e.answer.status not in [403, 404]:
                        raise
                    print(e)
                    continue
                datasets.append(gameData)
                gamesdone.add(gameId)
    except:
        traceback.print_last()
    finally:
        with open(progress_file, 'bw') as progress_fh:
            pickle.dump(gamesdone, progress_fh)
            pickle.dump(datasets, progress_fh)
        