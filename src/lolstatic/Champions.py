'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request
import lolstatic

idToChampion = {}

for patch in lolstatic.relevantVersions:
    championsAnswer = api_request("/api/lol/static-data/euw/v1.2/champion", version = patch)
    championsVersion = championsAnswer['version']
    nameToChampion = championsAnswer['data']
    idToChampion.update({nameToChampion[name]['id']:nameToChampion[name] for name in nameToChampion})
