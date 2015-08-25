'''
Created on 25.08.2015

@author: Katora
'''
from lolstatic import Items
'''
Updates the inventory according to the item bought (deletes items it is made from and adds it afterwards).
Returns all components that had to be bought for this to complete (including the item that was bought)
'''
def hasItem(inventory, itemId):
    return inventory[itemId]

def removeItem(inventory, itemId):
    inventory[itemId] = 0

def buyItem(inventory, itemBoughtId):
    buylist = []
    item = Items.idToItem[itemBoughtId]
    if 'from' in item:
        for component in item['from']:
            useComponentInCraft(inventory, int(component), buylist)
    inventory[itemBoughtId] += 1
    buylist.append(itemBoughtId)
    return buylist

def useComponentInCraft(inventory, itemId, buylist):
    """Notifies the inventory that the itemId is to craft
    another item with. If it exists in the inventory, remove it,
    else add it to the buy list and recurse.
    @param inventory: the inventory where crafting components may be in
    @param itemId: the item being used in a recipe
    @param buylist: a list with all items that weren't found in the inventory
    and had to be virtually bought
    """
    if not hasItem(inventory, itemId):
        buylist.append(itemId)
        item = Items.idToItem[itemId]
        if 'from' in item:
            for component in item['from']:
                useComponentInCraft(inventory, int(component), buylist)
    else:
        inventory[itemId] -= 1
