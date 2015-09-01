'''
Created on 29.08.2015

@author: Katora
'''
from lolstatic import getRegionEnum, getVersionEnum, RoleTypes, LaneTypes,\
    Versions, RegionTypes, QueueType, EloType
from lolstatic import Champions, Items, Maps
from analysis.AnalysisTree import AnalysisTree
from analysis.GameAnalysis import RateAnalyser, mergeTimeGoldSpreadJson,\
    timeGoldSpreadToJson
import os
import json
import pickle
import time
import gc
from collections import namedtuple
from analysis import SpecialCaseDefaultDict
from analysis.FileGuard import FileGuard
from multiprocessing.pool import ThreadPool

KeyTuple = namedtuple('KeyTuple', 'region version mapId queue elo championId itemId role lane')
ShortKeyTuple = namedtuple('ShortKeyTuple', 'region version mapId queue elo')
GroupedResults = namedtuple('GroupedResults', 'commonKey resultList')

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

def shortKeyTupleToPathAndFile(shortKeyt):
    folderNameTuple = (shortKeyt.region.value,
                       shortKeyt.version.value,
                       str(shortKeyt.mapId))
    fnTuple = (shortKeyt.queue.value,
                       shortKeyt.elo.value)
    return (os.path.join('..', 'data', 'analysis', *folderNameTuple), '{0}.{1}.json'.format(*fnTuple))

def saveGroupToFile(groupedResult):
    commonKey = groupedResult.commonKey
    resultList = groupedResult.resultList
    path, fileName = shortKeyTupleToPathAndFile(commonKey)
    fullPath = os.path.join(path, fileName)
    with fileguard.fileLock(fullPath):
        resourceDict = loadResourcesFromFile(fullPath)
        for key, timeGoldSpread in resultList:
            keytuple = KeyTuple(*key)
            resourceIdentifier = mapKeyToResourceIdentifier(keytuple)
            if resourceIdentifier in resourceDict:
                timeGoldSpread = mergeTimeGoldSpreadJson(timeGoldSpread, resourceDict[resourceIdentifier])
            resourceDict[resourceIdentifier] = timeGoldSpreadToJson(timeGoldSpread)
        saveResourcesToFile(path, fileName, resourceDict)

if __name__ == '__main__':
    
    dataSets = generateDataSetsFromFiles()
    #keyGeneratorList = (regions, versions, Maps.idToMap, queueTypes, eloTypes, Champions.idToChampion, Items.apItemIds, roleTypes, laneTypes) #region patch map queue champion item role lane
    anyValues = {1:LaneTypes.ANY, 2:RoleTypes.ANY, 3: 'ANY', 4: 'ANY', 5: EloType.ANY, 6: QueueType.ANY, 7: 'ANY', 8: Versions.ANY, 9: RegionTypes.ANY}
    analysisTree = AnalysisTree(9, RateAnalyser, anyValues)
    
    skipCounter = SavedObject(0, "../data/analysis/analysisCounter.pkl")
    
    print("Starting to analyze the data")
    
    doneCount = 0
    oneRuncount = 0
    
    def groupResultsChampItem(resultGen):
        comp = next(resultGen)
        partial = [comp]
        for result in resultGen:
            if not comp[0][4] == result[0][4]:
                commonKey = ShortKeyTuple(*comp[0][0:5])
                yield GroupedResults(commonKey, partial)
                partial = []
                comp = result
            partial.append(result)
        commonKey = ShortKeyTuple(*comp[0][0:5])
        yield GroupedResults(commonKey, partial)
    
    def doPartialSaveAndClear(setsDone):
        skipCounter.object += setsDone	#We increase the skip counter first to make sure that we don't count a data set twice, even if we skip data set when we crash
        print(analysisTree.result((RegionTypes.ANY, Versions.ANY, 'ANY', QueueType.ANY, EloType.ANY, 'ANY', 'ANY', RoleTypes.ANY, LaneTypes.ANY)))
        results = analysisTree.allResults()
        print('Saving data to file, please do not interrupt')
        groupedResults = groupResultsChampItem(results)
        with ThreadPool() as pool:
            pool.map(saveGroupToFile, groupedResults)
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
