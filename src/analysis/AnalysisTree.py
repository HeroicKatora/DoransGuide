'''
Created on 26.08.2015
@author: Katora
'''
from collections import Iterator
from collections import defaultdict

class Analyzer():
    ''' Accumulators take multiple sets of data and analyze them to then output a result.
    '''
    
    def analyze(self, data):
        '''Adds a new data set to the anaylzer
        '''
        pass
    
    def result(self):
        '''Returns the result of the accumulated data sets
        @invariant: The object itself should remain unchanged when calling this method
        '''
        pass

class AnalysisTree():
    ''' A tree designed to be quick on the analysis of multi dimensional data which is selected by non-comparable keys and not by range.
    Additionally, every set of keys has a value that is recognized as the any values, a value that means that all keys should be selected.
    Every layer of the tree holds a map from possible values to the trees of the layer below.
    '''
    
    def __init__(self, keyGeneratorList: list, analyzertype: type(Analyzer), anyvalues: dict = defaultdict(lambda:None)):
        '''
        @param keyGeneratorList: A list of generators that generate the keys for specific layers of the tree, needs to be subscriptable
        @param analyzertype: A default constructible type that is later used to analyze the date given to the tree
        @param anyvalues: A dictionary that maps from the remaining tree height to the value which should be used to represent the any key
        '''
        self.edgeDict = dict()
        self.height = len(keyGeneratorList)
        self.anyvalue = anyvalues[self.height]
        if not keyGeneratorList:
            self.analyzer = analyzertype()
            return
        for key in keyGeneratorList[0]:
            self.edgeDict[key] = AnalysisTree(keyGeneratorList[1:], analyzertype, anyvalues)
    
    def analyze(self, keyIterator:Iterator, data):
        '''Passes a data set onwards to the next layer of the tree. The right nodes are determined by the key from the iterable and the anyvalue supplied in the constructor.
        If this node is a leaf, passes the data on to its analyzer.
        '''
        if self.height:
            keys = {next(iter(keyIterator))}
            keys = (keys & {presentKey for presentKey in self.edgeDict}) | {self.anyvalue}
            for key in keys:
                self.edgeDict[key].analyze(keyIterator, data)
            return
        self.analyzer.analyze(data)
        pass
    
    def result(self, keyIterator:Iterator):
        '''Fetches the result from a specific key sequence's analyzer
        '''
        if self.height:
            key = next(iter(keyIterator))
            if key in self.edgeDict:
                return self.edgeDict[key].result(keyIterator)
            return None
        return self.analyzer.result()
