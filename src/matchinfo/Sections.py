print("Imported", __name__)
'''
Created on 25.08.2015
This module converts values to the corresponding interval indices
@author: Katora
'''
from bisect import bisect_left

possibleGoldValues = [x-7 for x in range(15)]
def getGoldSection(deltaGold, isTeamBlue):
    ind = bisect_left([3000*x for x in filter(lambda a:a, possibleGoldValues)], deltaGold)-7
    return ind if isTeamBlue else -ind

def getTimeSection(time):
    return bisect_left([1000*600*(x+1) for x in range(6)], time)
