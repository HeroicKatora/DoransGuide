'''
Created on 25.08.2015

@author: Katora
'''
from . import relevantVersions
from riotapi import getDownloader

idToChampion = {}

for patch in relevantVersions:
    dl = getDownloader()
    championsAnswer = dl.api_request("/api/lol/static-data/euw/v1.2/champion", version = patch)
    championsVersion = championsAnswer['version']
    nameToChampion = championsAnswer['data']
    idToChampion.update({nameToChampion[name]['id']:nameToChampion[name] for name in nameToChampion})
