'''
Created on 25.08.2015

@author: Katora
'''
from . import relevantVersions
from riotapi import getDownloader
from lolstatic import getVersionEnum, Versions
from collections import defaultdict

'''Holds the items for each patch. Version ANY contains the newest available data for each id
'''
versionToItems = defaultdict(dict) 

for patch in relevantVersions:
    dl = getDownloader()
    itemsAnswer = dl.api_request("/api/lol/static-data/euw/v1.2/item", itemListData = 'all', version = patch)
    itemsVersion = itemsAnswer['version']
    version = getVersionEnum(itemsVersion)
    nameToItem = itemsAnswer['data']
    versionToItems[version] = {nameToItem[name]['id']: nameToItem[name] for name in nameToItem}
    versionToItems[Versions.ANY].update(versionToItems[version])
    print("Gathered items for version ", version)

apItemIds = defaultdict(list)   #Maps item ids that are ap items to a list of patches in which they are
for version in Versions:
    itemsOfVersion = versionToItems[version]
    for itemId in itemsOfVersion:
        item = itemsOfVersion[itemId]
        if 'PercentMagicDamageMod' in item['stats'] or 'FlatMagicDamageMod' in item['stats']:
            apItemIds[itemId].append(version)
