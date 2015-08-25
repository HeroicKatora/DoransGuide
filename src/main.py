
#from matchinfo import loadGame
import json
import lolstatic

from matchinfo import Game
from matchinfo import item_events

file = open("../MatchExample.json", 'r')
fileAsString = "".join(file)
jsonOb = json.loads(fileAsString)

game = Game(jsonOb)
print(item_events(game))

