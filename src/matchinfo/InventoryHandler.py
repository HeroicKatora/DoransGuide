'''
Created on 25.08.2015

@author: Katora
'''
from lolstatic import Items, getVersionEnum, Versions
from collections import defaultdict

class Inventory(object):
    """Keeps the state of a player's inventory. Although it doesn't secure
    against inventory overflow
    """
    def __init__(self, patchString):
        self._items = defaultdict(int)
        self.version = getVersionEnum(patchString)

    def hasItem(self, itemId):
        """Checks if the player has at least one item with the specied id
        """
        return self._items[itemId] > 0
    
    def removeItem(self, itemId):
        """Removes one item of the specified id from the inventory.
        For example when the player drinks a potion
        """
        self._items[itemId] -= 1
    
    def buyItem(self, itemBoughtId):
        """
        Updates the inventory according to the item bought (deletes items it is made from and adds it afterwards).
        Returns all components that had to be bought for this to complete (including the item that was bought)
        @param itemBoughtId: the item that was bought
        """
        buylist = []
        item = Items.versionToItems[self.version][itemBoughtId]
        if 'from' in item:
            for component in item['from']:
                self._useComponentInCraft(int(component), buylist)
        self._items[itemBoughtId] += 1
        buylist.append(itemBoughtId)
        return buylist
    
    def _useComponentInCraft(self, itemId, buylist):
        """Notifies the inventory that the itemId is to craft
        another item with. If it exists in the inventory, remove it,
        else add it to the buy list and recurse.
        @param itemId: the item being used in a recipe
        @param buylist: a list with all items that weren't found in the inventory
        and had to be virtually bought
        """
        if not self.hasItem(itemId):
            buylist.append(itemId)
            item = Items.versionToItems[self.version][itemId]
            if 'from' in item:
                for component in item['from']:
                    self._useComponentInCraft(int(component), buylist)
        else:
            self._items[itemId] -= 1
