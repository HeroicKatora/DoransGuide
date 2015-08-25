'''
import json

from matchinfo import Game
from matchinfo import item_events

file = open("../MatchExample.json", 'r')
fileAsString = "".join(file)
jsonOb = json.loads(fileAsString) #These are about 31k bytes

game = Game(jsonOb)
'''
