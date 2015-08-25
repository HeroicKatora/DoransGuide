'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request

championsAnswer = api_request("/api/lol/static-data/euw/v1.2/champion")
championsVersion = championsAnswer['version']
nameToChampion = championsAnswer['data']
idToChampion = {nameToChampion[name]['id']:nameToChampion[name] for name in nameToChampion}
