'''
Created on 25.08.2015

@author: Katora
'''

from . import relevantVersions
from riotapi import getDownloader

idToMap = {}

for patch in relevantVersions:
    dl = getDownloader('na')
    mapAnswer = dl.api_request('na', "/api/lol/static-data/euw/v1.2/map", version = patch)
    itemsVersion = mapAnswer['version']
    nameToMap = mapAnswer['data']
    idToMap.update({nameToMap[name]['id']:nameToMap[name] for name in nameToMap})
