'''
Created on 26.08.2015
@author: Katora
'''
import itertools
from collections import Iterator, namedtuple
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

AnalysisResult = namedtuple('AnalysisResult', 'key value')

class AnalysisTree():
    ''' A tree designed to be quick on the analysis of multi dimensional data which is selected by non-comparable keys and not by range.
    Additionally, every set of keys has a value that is recognized as the any values, a value that means that all keys should be selected.
    Every layer of the tree holds a map from possible values to the trees of the layer below.
    '''
    
    def __init__(self, height, analyzertype: type(Analyzer), anyvalues: dict = defaultdict(lambda:None)):
        '''Constructor to recursively construct an analysis tree
        @param analyzertype: A default constructible type that is later used to analyze the date given to the tree
        @param anyvalues: A dictionary that maps from the remaining tree height to the value which should be used to represent the any key
        '''
        self.edgeDict = dict()
        self.height = height
        self.analyzerType = analyzertype
        self.anyvalues = anyvalues
        if not self.height:
            self.analyzer = analyzertype()
            return
        self.anyvalue = anyvalues[self.height]
        self.edgeDict = dict()
        self.edgeDict[self.anyvalue] = AnalysisTree(self.height-1, self.analyzerType, self.anyvalues)
    
    def analyze(self, keyTuple, data):
        '''Passes a data set onwards to the next layer of the tree. The right nodes are determined by the key from the iterable and the anyvalue supplied in the constructor.
        If this node is a leaf, passes the data on to its analyzer.
        '''
        if self.height:
            key , rest = keyTuple[0], keyTuple[1:]
            if not key in self.edgeDict:
                self.edgeDict[key] = AnalysisTree(self.height-1, self.analyzerType, self.anyvalues)
            self.edgeDict[key].analyze(rest, data)
            if not key == self.anyvalue:
                self.edgeDict[self.anyvalue].analyze(rest, data)
            return
        self.analyzer.analyze(data)
    
    def result(self, keyTuple):
        '''Fetches the result from a specific key sequence's analyzer
        '''
        if self.height:
            key, rest = keyTuple[0], keyTuple[1:]
            try:
                return self.edgeDict[key].result(rest)
            except KeyError:
                return None
        return self.analyzer.result()

    def allResults(self):
        '''Returns a dictionary with all the results in this tree
        '''
        if self.height:
            for key in self.edgeDict:
                for result in self.edgeDict[key].allResults():
                    yield AnalysisResult((key,)+result.key, result.value)
            return
        yield AnalysisResult(tuple(), self.analyzer.result())
        
    def clear(self):
        self.edgeDict.clear()
