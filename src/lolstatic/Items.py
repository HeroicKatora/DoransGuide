print("Imported", __name__)
'''
Created on 25.08.2015

@author: Katora
'''
from . import relevantVersions
from riotapi import getDownloader

idToItem = {}

for patch in relevantVersions:
    dl = getDownloader('na')
    itemsAnswer = dl.api_request('na', "/api/lol/static-data/euw/v1.2/item", itemListData = 'all', version = patch)
    itemsVersion = itemsAnswer['version']
    nameToItem = itemsAnswer['data']
    idToItem.update({nameToItem[name]['id']: nameToItem[name] for name in nameToItem})

apItemIds = filter(lambda item: idToItem[item]['stats']['PercentMagicDamageMod'] or idToItem[item]['stats']['FlatMagicDamageMod'],
                   [itemid for itemid in idToItem])
