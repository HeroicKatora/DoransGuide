'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request
import lolstatic

idToMap = {}

for patch in lolstatic.relevantVersions:
    mapAnswer = api_request("/api/lol/static-data/euw/v1.2/map", version = patch)
    itemsVersion = mapAnswer['version']
    nameToMap = mapAnswer['data']
    idToMap.update({nameToMap[name]['id']:nameToMap[name] for name in nameToMap})
