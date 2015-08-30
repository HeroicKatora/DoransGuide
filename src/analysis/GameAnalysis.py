'''
Created on 27.08.2015

@author: Katora
'''
from analysis.AnalysisTree import Analyzer, AnalysisTree
from collections import namedtuple
from matchinfo.Sections import anyValueTime, anyValueGold, possibleGoldValues,\
    possibleTimeValues, getTimeSection, getGoldSection
from itertools import product

WinStatistic = namedtuple("WinStatistic", "gameCount gamesWon")
TimeGoldSpread = namedtuple("TimeGoldSpread", "timeAndGoldTable timeTable goldTable winStatistic")

def keyFromDataset(dataset):
    '''Constructs a key from a given dataset, this for example converts the timestamps to time intervals etc
    '''
    pass

class WinAnalyser(Analyzer):
    
    def __init__(self):
        self.gameCount = 0
        self.gamesWon = 0
        
    
    def analyze(self, data):
        self.gameCount+=1
        if data.winner:
            self.gamesWon += 1
    
    def result(self):
        return WinStatistic(self.gameCount, self.gamesWon)


class RateAnalyser(WinAnalyser):
    
    def __init__(self):
        WinAnalyser()
        self.timeAndGold = AnalysisTree([possibleGoldValues, possibleTimeValues], WinAnalyser, {1: anyValueTime, 2: anyValueGold})
        
    
    def analyze(self, data):
        WinAnalyser.analyze(self, data)
        timeStep = getTimeSection(data.timeStamp)
        goldDiff = getGoldSection(data.goldDiff)
        self.timeAndGold.analyze((goldDiff, timeStep), data)
    
    def result(self):
        timeAndGoldTable = [self.timeAndGold.result(keys) for keys in product(possibleGoldValues, possibleTimeValues)]
        timeTable = [self.timeAndGold.result(keys) for keys in product(anyValueGold, possibleTimeValues)]
        goldTable = [self.timeAndGold.result(keys) for keys in product(possibleGoldValues, anyValueTime)]
        winStatistic = self.timeAndGold.result((anyValueGold, anyValueTime))
        return TimeGoldSpread(timeAndGoldTable, timeTable, goldTable, winStatistic)
