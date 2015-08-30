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

def mergeTimeGoldSpreadJson(tgs1, tgs2AsJson):
    tgs2 = TimeGoldSpread(*tgs2AsJson)
    return TimeGoldSpread([mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.timeAndGoldTable, tgs2.timeAndGoldTable)],
                          [mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.timeTable, tgs2.timeTable)],
                          [mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.goldTable, tgs2.goldTable)],
                          mergeWinStatisticsJson(tgs1.winStatistic, tgs2.winStatistic))

def mergeWinStatisticsJson(ws1, ws2AsJson):
    ws2 = WinStatistic(*ws2AsJson)
    return WinStatistic(ws1.gameCount+ws2.gameCount, ws1.gamesWon+ws2.gamesWon)

def keyFromDataset(dataset):
    '''Constructs a key from a given dataset, this for example converts the timestamps to time intervals etc
    '''
    pass

class WinAnalyser(Analyzer):
    
    def __init__(self):
        self.gameCount = 0
        self.gamesWon = 0
        
    
    def analyze(self, data):
        self.gameCount += 1
        if data.winner.value:
            self.gamesWon += 1
    
    def result(self):
        return WinStatistic(self.gameCount, self.gamesWon)


class RateAnalyser(WinAnalyser):
    
    def __init__(self):
        super(RateAnalyser, self).__init__()
        self.timeAndGold = AnalysisTree(2, WinAnalyser, {1: anyValueTime, 2: anyValueGold})
        
    
    def analyze(self, data):
        WinAnalyser.analyze(self, data)
        timeStep = getTimeSection(data.timeStamp)
        goldDiff = getGoldSection(data.goldDiff)
        if goldDiff == 7:
            print(data.goldDiff)
        self.timeAndGold.analyze((goldDiff, timeStep), data)
    
    def result(self):
        timeAndGoldTable = [self.timeAndGold.result(keys) for keys in product(possibleGoldValues, possibleTimeValues)]
        timeTable = [self.timeAndGold.result(keys) for keys in product((anyValueGold,), possibleTimeValues)]
        goldTable = [(self.timeAndGold.result(keys), keys) for keys in product(possibleGoldValues, (anyValueTime,))]
        winStatistic = self.timeAndGold.result((anyValueGold, anyValueTime))
        return TimeGoldSpread(timeAndGoldTable, timeTable, goldTable, winStatistic)
