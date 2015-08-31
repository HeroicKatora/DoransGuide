from _collections import defaultdict


class SpecialCaseDefaultDict(defaultdict):
    '''A special defaultdict that is the identity function for all non existent keys and a dictionary else. 
    '''
    
    def __init__(self, diction):
        self.update(diction)
    
    def __missing__(self, key):
        return key
