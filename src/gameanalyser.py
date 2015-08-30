'''
Created on 29.08.2015

@author: Katora
'''
from lolstatic import *
from lolstatic import Champions, Items, Maps
from analysis.AnalysisTree import AnalysisTree
from analysis.GameAnalysis import RateAnalyser, mergeTimeGoldSpreadJson, TimeGoldSpread
import os
import json
import pickle
import time
from collections import namedtuple

KeyTuple = namedtuple('KeyTuple', 'region version mapId queue elo championId itemId role lane')

def mapDataToKey(itemBuy):
    return KeyTuple(getRegionEnum(itemBuy.region), 
            getVersionEnum(itemBuy.patch),
            itemBuy.mapId,
            itemBuy.queueType,
            itemBuy.participantElo,
            itemBuy.champion,
            itemBuy.itemId,
            RoleTypes.ANY,
            LaneTypes.ANY)  #Can't really handle that much information without a database, so we leave it out atm

def generateDataSetsFromFiles():
    for fileName in os.listdir('../data/raw') :
        if not fileName.startswith('data_'):
            continue
        with open(os.path.join('../data/raw', fileName), 'br') as file:
            for singleSet in pickle.load(file):
                yield singleSet
    return 

def mapKeyToPath(keyt):
    folderNameTuple = (keyt.region.value,
                       keyt.version.value,
                       str(keyt.mapId),
                       keyt.queue.value,
                       keyt.elo.value,
                       str(keyt.championId),
                       str(keyt.itemId),
                       keyt.role.value,
                       keyt.lane.value)
    return os.path.join("..", "data", *folderNameTuple)

def saveToFile(key, timeGoldSpread):
    path = mapKeyToPath(KeyTuple(*key))
    if not os.path.exists(path):
        os.makedirs(path)
    fullPath = os.path.join(path, "data.json")
    if os.path.exists(fullPath):
        with open(fullPath, 'r') as existingDataFile:
            existingData = json.load(existingDataFile)
            timeGoldSpread = mergeTimeGoldSpreadJson(timeGoldSpread, existingData)
    with open(fullPath, 'w') as file:
        json.dump(timeGoldSpread, file)

if __name__ == '__main__':
    dataSets = generateDataSetsFromFiles()
    keyGeneratorList = (regions, versions, Maps.idToMap, queueTypes, eloTypes, Champions.idToChampion, Items.idToItem, roleTypes, laneTypes) #region patch map queue champion item role lane
    anyValues = {1:LaneTypes.ANY, 2:RoleTypes.ANY, 3: 'ANY', 4: 'ANY', 5: EloType.ANY, 6: QueueType.ANY, 7: 'ANY', 8: Versions.ANY, 9: RegionTypes.ANY}
    analysisTree = AnalysisTree(len(keyGeneratorList), RateAnalyser, anyValues)
    
    print("Starting to analyze the data")
    
    def doPartialSaveAndClear():
        #print(analysisTree.result((RegionTypes.ANY, Versions.ANY, 'ANY', QueueType.ANY, EloType.ANY, 'ANY', 'ANY', RoleTypes.ANY, LaneTypes.ANY)))
        results = analysisTree.allResults()
        for resultTuple in results:
            saveToFile(resultTuple.key, resultTuple.value)
        analysisTree.clear()
    
    def shouldAnalyze(dataSet):
        return dataSet.itemId in Items.apItemIds
    
    print('Ap item ids: ' , Items.apItemIds)
    lastTime = time.time()
    doneCount = 0
    oneRuncount = 0
    for data in dataSets:
        if not shouldAnalyze(data):
            continue
        analysisTree.analyze(mapDataToKey(data), data)
        doneCount += 1
        oneRuncount += 1
        if oneRuncount > 10000:
            doPartialSaveAndClear()
            oneRuncount = 0
        if time.time()-lastTime > 10:
            print("{0} data sets analyzed".format(doneCount))
            lastTime = time.time()
    
    doPartialSaveAndClear()
    print("All data sets are now analysed")
    print("Analysis saved to disk")
