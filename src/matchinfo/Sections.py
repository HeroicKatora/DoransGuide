'''
Created on 25.08.2015
This module converts values to the corresponding interval indices
@author: Katora
'''
from bisect import bisect_left

possibleGoldValues = [x-7 for x in range(15)]
anyValueGold = None

def getGoldSection(deltaGold, isTeamBlue):
    """Gets the section number in which the specified gold differential falls
    @param deltaGold: the gold diff, GoldTeamBlue - GoldTeamRed
    @param isTeamBlue: whether the gold section is computed for the red or
    the blue team.
    """
    ind = bisect_left([3000*x for x in filter(lambda a:a, possibleGoldValues)], deltaGold)-7
    return ind if isTeamBlue else -ind

possibleTimeValues = [x for x in range(7)]
anyValueTime = None

def getTimeSection(time):
    """Gets the time section in which the specific time falls
    @param time: the current time in seconds since the start of the game
    """
    return bisect_left([1000*600*(x+1) for x in range(6)], time)
