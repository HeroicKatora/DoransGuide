'''
Created on 25.08.2015

@author: Katora
'''
from . import relevantVersions
from riotapi import getDownloader

idToChampion = {}

for patch in relevantVersions:
    dl = getDownloader('na')
    championsAnswer = dl.api_request('na', "/api/lol/static-data/euw/v1.2/champion", version = patch)
    championsVersion = championsAnswer['version']
    nameToChampion = championsAnswer['data']
    idToChampion.update({nameToChampion[name]['id']:nameToChampion[name] for name in nameToChampion})
