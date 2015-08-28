'''
Created on 27.08.2015

@author: Katora
'''
from analysis.AnalysisTree import Analyzer
from collections import namedtuple

WinStatistics = namedtuple("WinStatistics", "gameCount gamesWon")

def keyFromDataset(dataset):
    '''Constructs a key from a given dataset, this for example converts the timestamps to time intervals etc
    '''

class GameAnalyser(Analyzer):
    
    def __init__(self):
        self.gameCount = 0
        self.gamesWon = 0
        
    
    def analyze(self, data):
        self.gameCount+=1
        if data.winner:
            self.gamesWon += 1
    
    def result(self):
        return WinStatistics(self.gameCount, self.gamesWon)
