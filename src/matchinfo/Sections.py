'''
Created on 25.08.2015
This module converts values to the corresponding interval indices
@author: Katora
'''
from bisect import bisect_left

possibleGoldValues = [x-7 for x in range(15)]
goldSections = [3000*x for x in possibleGoldValues if not x == 0]
anyValueGold = None

def getGoldSection(deltaGold):
    """Gets the section number in which the specified gold differential falls
    @param deltaGold: the gold diff, GoldTeamSelf - GoldTeamEnemy
    """
    ind = bisect_left(goldSections, deltaGold)-7
    return ind

possibleTimeValues = [x for x in range(7)]
timeSections = [1000*600*(x+1) for x in range(6)]
anyValueTime = None

def getTimeSection(time):
    """Gets the time section in which the specific time falls
    @param time: the current time in seconds since the start of the game
    """
    return bisect_left(timeSections, time)
