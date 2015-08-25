'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request

itemsAnswer = api_request("/api/lol/static-data/euw/v1.2/item", itemListData = 'all', version = '5.11.1')
itemsVersion = itemsAnswer['version']
nameToItem = itemsAnswer['data']
idToItem = {nameToItem[name]['id']: nameToItem[name] for name in nameToItem}
