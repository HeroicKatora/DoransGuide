'''
Created on 29.08.2015

@author: Katora
'''
from lolstatic import regions, versions, queueTypes,\
    laneTypes, roleTypes, eloTypes, regions, availableMaps
from lolstatic import Items, Champions
from analysis.AnalysisTree import AnalysisTree
from analysis.GameAnalysis import RateAnalyser
import os
import json
import pickle

def mapDataToKey(itemBuy):
    pass

def loadDataFiles():
    datasets = []
    for fileName in os.listdir('../data/raw') :
        if not fileName.startswith('data'):
            continue
        with open(fileName) as file:
            datasets.extend(pickle.load(file))
    return datasets

def mapKeyToPath(key):
    return os.path.join("..", "data", *map(key))

def saveToFile(key, timeGoldSpread):
    path = mapKeyToPath(key)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "data.json"), 'w') as file:
        json.dump(timeGoldSpread, file)

if __name__ == '__main__':
    dataSets = loadDataFiles()
    keyGeneratorList = tuple(regions, versions, availableMaps, queueTypes, eloTypes, Champions.idToChampion, Items.idToItem, roleTypes, laneTypes) #region patch map queue champion item role lane
    anyValues = {}
    analysisTree = AnalysisTree(keyGeneratorList, RateAnalyser, anyValues)
    for data in dataSets:
        analysisTree.analyze(mapDataToKey(data), data)
    
    print("All data sets are now analysed")
    
    results = analysisTree.allResults()
    for analysedKey in results:
        saveToFile(analysedKey, results[analysedKey])
    
    print("Analysis saved to disk")
