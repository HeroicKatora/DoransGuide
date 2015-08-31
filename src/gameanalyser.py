'''
Created on 29.08.2015

@author: Katora
'''
from lolstatic import *
from lolstatic import Champions, Items, Maps
from analysis.AnalysisTree import AnalysisTree
from analysis.GameAnalysis import RateAnalyser, mergeTimeGoldSpreadJson, TimeGoldSpread, newTimeGoldSpread
import os
import json
import pickle
import time
import gc
from hashlib import sha256
from collections import namedtuple
from analysis import SpecialCaseDefaultDict
from analysis.FileGuard import FileGuard
from multiprocessing.pool import ThreadPool

KeyTuple = namedtuple('KeyTuple', 'region version mapId queue elo championId itemId role lane')
def keyTupleSortKey(el):
    '''Returns a new key tuple that can be used to sort the key tuple el in a list
    '''
    return (el.region, el.patch, el.mapId, el.queueType.value, el.participantElo.value, el.champion, el.itemId)

class SavedObject():
    def __init__(self, objectToGuard, filepath):
        self.object = objectToGuard
        self.filepath = filepath
        try:
            with open(filepath, 'br') as file:
                self.object = pickle.load(file)
        except Exception:
            pass

    def __enter__(self):
        pass
    
    def __exit__(self, type, value, traceback):
        dirs = os.path.split(self.filepath)[0]
        if not os.path.exists(dirs):
            os.makedirs(dirs, exist_ok = True)
        with open(self.filepath, 'bw') as file:
            pickle.dump(self.object, file)

mappingsForMap = SpecialCaseDefaultDict({1:11})

def mapDataToKey(itemBuy):
    return KeyTuple(getRegionEnum(itemBuy.region), 
            getVersionEnum(itemBuy.patch),
            mappingsForMap[itemBuy.mapId],
            itemBuy.queueType,
            itemBuy.participantElo,
            itemBuy.champion,
            itemBuy.itemId,
            RoleTypes.ANY,
            LaneTypes.ANY)  #Can't really handle that much information without a database, so we leave it out atm

def generateDataSetsFromFiles():
    availableFiles = os.listdir('../data/raw')
    availableFiles.sort()
    for fileName in availableFiles:
        if not fileName.startswith('data_'):
            continue
        with open(os.path.join('../data/raw', fileName), 'br') as file:
            setList = pickle.load(file)
            setList.sort(key = keyTupleSortKey)
            for singleSet in setList:
                yield singleSet
    return 

def mapKeyToResourceIdentifier(keyt):
    folderNameTuple = (keyt.region.value,
                       keyt.version.value,
                       str(keyt.mapId),
                       keyt.queue.value,
                       keyt.elo.value,
                       str(keyt.championId),
                       str(keyt.itemId),
                       keyt.role.value,
                       keyt.lane.value)
    return os.path.join(*folderNameTuple)

def mapResourceIdentifierToPathAndFile(rI):
    '''A file path and file anem is generate for a resource identifier by encoding it in utf-8 and hashing it with sha256.
    Then the first 2 hexcharacters (8 bits) are taken as the directory name inside of data/analysis and the next 6 bits as
    the file name (as 2 hex characters). The file extension is json.
    Thus we split around 1m (2^20) identifiers (nearly) uniformly to 2^14 files leaving 2^6 data sets in one file, which
    equals around 50-140kB. This should be parseable and at the same time be manageable by git. Cashing might lower the penalty for the client.
    '''
    hasher = sha256()
    hasher.update(bytearray(rI, 'utf-8'))
    hashnumber = hasher.digest()
    return (os.path.join('..', 'data', 'analysis', '{0:02x}'.format(hashnumber[0])), '{0:02x}.json'.format(hashnumber[1]&0xFC))

fileguard = FileGuard()

def loadResourcesFromFile(filepath):
    '''Loads a resource dictionary from the given file
    If the file is not found, returns an empty dictionary.
    '''
    existingDict = dict()
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            existingDict = json.load(file)
    return existingDict

def saveResourcesToFile(path, fileName, resourceDict):
    '''Save the TimeAndSpread to a given file.
    '''
    if not os.path.exists(path):
        os.makedirs(path, exist_ok = True)
    filepath = os.path.join(path, fileName)
    with open(filepath, 'w') as file:
        json.dump(resourceDict, file)

def saveToFile(key, timeGoldSpread):
    resourceIdentifier = mapKeyToResourceIdentifier(KeyTuple(*key))
    path, fileName = mapResourceIdentifierToPathAndFile(resourceIdentifier)
    fullPath = os.path.join(path, fileName)
    with fileguard.fileLock(fullPath):
        resourceDict = loadResourcesFromFile(fullPath)
        if resourceIdentifier in resourceDict:
            timeGoldSpread = mergeTimeGoldSpreadJson(timeGoldSpread, resourceDict[resourceIdentifier])
        resourceDict[resourceIdentifier] = timeGoldSpread
        saveResourcesToFile(path, fileName, resourceDict)

if __name__ == '__main__':
    
    dataSets = generateDataSetsFromFiles()
    keyGeneratorList = (regions, versions, Maps.idToMap, queueTypes, eloTypes, Champions.idToChampion, Items.apItemIds, roleTypes, laneTypes) #region patch map queue champion item role lane
    anyValues = {1:LaneTypes.ANY, 2:RoleTypes.ANY, 3: 'ANY', 4: 'ANY', 5: EloType.ANY, 6: QueueType.ANY, 7: 'ANY', 8: Versions.ANY, 9: RegionTypes.ANY}
    analysisTree = AnalysisTree(len(keyGeneratorList), RateAnalyser, anyValues)
    
    skipCounter = SavedObject(0, "../data/analysis/analysisCounter.pkl")
    
    print("Starting to analyze the data")
    
    doneCount = 0
    oneRuncount = 0
    
    def doPartialSaveAndClear(setsDone):
        skipCounter.object += setsDone	#We increase the skip counter first to make sure that we don't count a data set twice, even if we skip data set when we crash
        print(analysisTree.result((RegionTypes.ANY, Versions.ANY, 'ANY', QueueType.ANY, EloType.ANY, 'ANY', 'ANY', RoleTypes.ANY, LaneTypes.ANY)))
        results = analysisTree.allResults()
        print('Saving data to file, please do not interrupt')
        with ThreadPool() as pool:
            pool.starmap(saveToFile, results)
        analysisTree.clear()
        gc.collect()
        print('Everthing is saved')
    
    def shouldAnalyze(dataSet):
        return dataSet.itemId in Items.apItemIds
    
    print('Ap item ids: ' , Items.apItemIds)
    with skipCounter:
        lastTime = time.time()
        for data in dataSets:
            if not shouldAnalyze(data):
                continue
            if doneCount < skipCounter.object:
                doneCount += 1
                continue
            analysisTree.analyze(mapDataToKey(data), data)
            doneCount += 1
            oneRuncount += 1
            #Increase or decrease this number according to the memory available to you. This is for ~1GiB
            if oneRuncount > 20000:
                doPartialSaveAndClear(oneRuncount)
                oneRuncount = 0
            if time.time()-lastTime > 10:
                print("{0} data sets analyzed".format(doneCount))
                lastTime = time.time()
        
        doPartialSaveAndClear(oneRuncount)
        print("All data sets are now analysed")
        print("Analysis saved to disk")
