'''
Created on 25.08.2015

@author: Katora
'''

from . import relevantVersions
from riotapi import getDownloader

idToMap = {}
nameToMap = {}

for patch in relevantVersions:
    dl = getDownloader()
    mapAnswer = dl.api_request("/api/lol/static-data/euw/v1.2/map", version = patch)
    itemsVersion = mapAnswer['version']
    identifierToMap = mapAnswer['data']
    idToMap.update({int(identifierToMap[name]['mapId']):identifierToMap[name] for name in identifierToMap})
    nameToMap.update({idToMap[id]['mapName']:idToMap[id] for id in idToMap})
