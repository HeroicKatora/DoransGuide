'''
Created on 25.08.2015

@author: Katora
'''

from . import relevantVersions
from riotapi import getDownloader

idToMap = {}

for patch in relevantVersions:
    dl = getDownloader()
    mapAnswer = dl.api_request("/api/lol/static-data/euw/v1.2/map", version = patch)
    itemsVersion = mapAnswer['version']
    nameToMap = mapAnswer['data']
    idToMap.update({nameToMap[name]['id']:nameToMap[name] for name in nameToMap})
