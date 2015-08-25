'''
Created on 25.08.2015

@author: Katora
'''
from bisect import bisect_left

def contains(olist, x):
    return indexOf(olist, x) >= 0

def indexOf(olist, x):
    pos = bisect_left(olist, x)
    return pos if pos < len(olist) and olist[pos] == x else -1

def remove(olist, x):
    i = indexOf(olist, x)
    olist[i:i+1] = []
    return i >= 0
