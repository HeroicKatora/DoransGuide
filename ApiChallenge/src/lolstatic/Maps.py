'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request

mapAnswer = api_request("/api/lol/static-data/euw/v1.2/map")
itemsVersion = mapAnswer['version']
nameToMap = mapAnswer['data']
idToMap = {nameToMap[name]['id']:nameToMap[name] for name in nameToMap}
