'''
Created on 25.08.2015

@author: Katora
'''
from . import relevantVersions
from riotapi import getDownloader

idToItem = {}

for patch in relevantVersions:
    dl = getDownloader()
    itemsAnswer = dl.api_request("/api/lol/static-data/euw/v1.2/item", itemListData = 'all', version = patch)
    itemsVersion = itemsAnswer['version']
    nameToItem = itemsAnswer['data']
    idToItem.update({nameToItem[name]['id']: nameToItem[name] for name in nameToItem})

apItemIds = [x for x in filter(lambda item: 'PercentMagicDamageMod' in idToItem[item]['stats'] or 'FlatMagicDamageMod' in idToItem[item]['stats'],
                   idToItem)]
