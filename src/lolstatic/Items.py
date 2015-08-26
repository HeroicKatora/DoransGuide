'''
Created on 25.08.2015

@author: Katora
'''
from riotapi import api_request
import lolstatic

idToItem = {}

for patch in lolstatic.relevantVersions:
    itemsAnswer = api_request('na', "/api/lol/static-data/euw/v1.2/item", itemListData = 'all', version = patch)
    itemsVersion = itemsAnswer['version']
    nameToItem = itemsAnswer['data']
    idToItem.update({nameToItem[name]['id']: nameToItem[name] for name in nameToItem})

apItemIds = filter(lambda item: idToItem[item]['stats']['PercentMagicDamageMod'] or idToItem[item]['stats']['FlatMagicDamageMod'],
                   [itemid for itemid in idToItem])
