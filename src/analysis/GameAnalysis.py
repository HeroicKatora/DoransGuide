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
    if not tgs2AsJson: return tgs1
    tgs2 = TimeGoldSpread(*tgs2AsJson)
    if not tgs1: return tgs2
    return TimeGoldSpread([mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.timeAndGoldTable, tgs2.timeAndGoldTable)],
                          [mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.timeTable, tgs2.timeTable)],
                          [mergeWinStatisticsJson(el[0], el[1]) for el in zip(tgs1.goldTable, tgs2.goldTable)],
                          mergeWinStatisticsJson(tgs1.winStatistic, tgs2.winStatistic))

def mergeWinStatisticsJson(ws1, ws2AsJson):
    if not ws2AsJson: return ws1
    ws2 = WinStatistic(*ws2AsJson)
    if not ws1: return ws2
    return WinStatistic(ws1.gameCount+ws2.gameCount, ws1.gamesWon+ws2.gamesWon)

def timeGoldSpreadToJson(tgs):
    return ([winStatisticToJson(ws) for ws in tgs.timeAndGoldTable],
            [winStatisticToJson(ws) for ws in tgs.timeTable],
            [winStatisticToJson(ws) for ws in tgs.goldTable],
            winStatisticToJson(tgs.winStatistic))

def winStatisticToJson(ws):
    if not ws: return None
    return (ws.gameCount, ws.gamesWon)

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
        self.timeAndGold.analyze((goldDiff, timeStep), data)
    
    def result(self):
        timeAndGoldTable = [self.timeAndGold.result(keys) for keys in product(possibleGoldValues, possibleTimeValues)]
        timeTable = [self.timeAndGold.result(keys) for keys in product((anyValueGold,), possibleTimeValues)]
        goldTable = [self.timeAndGold.result(keys) for keys in product(possibleGoldValues, (anyValueTime,))]
        winStatistic = self.timeAndGold.result((anyValueGold, anyValueTime))
        return TimeGoldSpread(timeAndGoldTable, timeTable, goldTable, winStatistic)
