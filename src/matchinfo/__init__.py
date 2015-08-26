from riotapi import api_request, AnswerException
from enum import Enum
from lolstatic import EloType, Items, itemEventTypes, FrameEventType, QueueType
from collections import defaultdict, namedtuple
from functools import partial
from matchinfo.InventoryHandler import removeItem, buyItem
from copy import copy
from matchinfo.Sections import getGoldSection, getTimeSection

'''
Exported method that loads a game from a region and a game identifier. Returns the game
'''
def loadGame(region, gameID):
    gameAnswer = api_request(region, '/api/lol/{region}/v2.2/match/{matchId}'.format(region = region, matchId = gameID), includeTimeline = True)
    return Game(gameAnswer)
    
class Winner(Enum):
    Blue = True
    Red = False

ItemBuy = namedtuple("ItemBuy", "itemId eventType champion mapId queueType participantElo goldDiff timeStamp winner")

class Game(object):
    """Wrapper for the data of a game, including its timeline,
    the teams, the region it took place in, the queue type, the map, the winner
    as well as the elo of the participants
    """
    def __init__(self, json):
        self.timeline = json['timeline']['frames']
        self.teamBlue = json['teams'][0]
        self.teamRed = json['teams'][1]
        self.region = json['region']
        self.queueType = QueueType(json['queueType'])
        self.mapId = json['mapId']
        self.teamBlueId = self.teamBlue['teamId']
        self.teamRedId = self.teamRed['teamId']
        self.winner = self.teamBlueId if self.teamBlue['winner'] else self.teamRedId
        self.participantToTeam = {part['participantId']: part['teamId'] for part in json['participants']}
        self.participantToChamp = {part['participantId']: part['championId'] for part in json['participants']}
        self.participantToElo = defaultdict(lambda:EloType.ANY)
        self.summonerIdToParticipant = defaultdict(lambda:0)
        self.summonerIdToParticipant.update({p['player']['summonerId']:p['participantId'] for p in json['participantIdentities'] if 'player' in p})
        if self.summonerIdToParticipant:
            try:
                ans = api_request(self.region.lower, "/api/lol/{region}/v2.5/league/by-summoner/{summonerId}/entry".format(region = self.region.lower(),
                        summonerId = ",".join(str(p) for p in self.summonerIdToParticipant)))
                summonerToRanking = {summonerId:defaultdict(lambda:EloType.UNRANKED, {QueueType(ranking['queue']):EloType(ranking['tier']) for ranking in ans[str(summonerId)]} 
                                                                                        if str(summonerId) in ans else dict()) 
                                    for summonerId in self.summonerIdToParticipant}
                self.participantToElo.update({self.summonerIdToParticipant[summId]: summonerToRanking[summId][self.queueType] for summId in self.summonerIdToParticipant})
            except AnswerException as e:
                if e.answer.status == 404:
                    self.participantToElo.update({self.summonerIdToParticipant[summonerId]:EloType.UNRANKED for summonerId in self.summonerIdToParticipant})
                else:
                    raise

'''
Analyses a whole game, going through the timeline frame by frame, and extracts information about items.
It returns a list of all item related action that where not undone in the shop directly afterwards.
Each action features certain stats, see the class ItemBuy for a list of those.
'''
def item_events(game):
    itemEvents = []
    inventoryStacks = defaultdict(list)
    inventories = defaultdict(lambda:defaultdict(int))
    gold = defaultdict(int)
    for frame in game.timeline:
        gold[game.teamBlueId] = 0
        gold[game.teamRedId] = 0
        for player in frame['participantFrames']:
            goldInc = frame['participantFrames'][player]['totalGold']
            gold[game.participantToTeam[int(player)]] += goldInc
        if 'events' not in frame:
            continue
        for itemEvent in filter(lambda x: x['eventType'] in itemEventTypes and x['participantId'], frame['events']):
            participant = itemEvent['participantId']
            inv = inventories[participant]
            stack = inventoryStacks[participant]
            eventtype = FrameEventType(itemEvent['eventType'])
            teamId = game.participantToTeam[participant]
            winningTeam = Winner(game.winner == teamId)
            goldDiff = getGoldSection(gold[game.teamBlueId]-gold[game.teamRedId], teamId == game.teamBlueId)
            timeStamp = getTimeSection(itemEvent['timestamp'])
            
            if eventtype == FrameEventType.ITEM_DESTROYED:
                itemId = itemEvent['itemId']
                itemEvents.append([ItemBuy(itemId,
                                           eventtype,
                                           game.participantToChamp[participant],
                                           game.mapId,
                                           game.queueType,
                                           game.participantToElo[participant],
                                           goldDiff,
                                           timeStamp,
                                           winningTeam)])
                stack.append(copy(inv))
                removeItem(inv, itemId)
            elif eventtype == FrameEventType.ITEM_SOLD:
                itemId = itemEvent['itemId']
                itemEvents.append([ItemBuy(itemId,
                                           eventtype,
                                           game.participantToChamp[participant],
                                           game.mapId,
                                           game.queueType,
                                           game.participantToElo[participant],
                                           goldDiff,
                                           timeStamp,
                                           winningTeam)])
                stack.append(copy(inv))
                removeItem(inv, itemId)
            elif eventtype == FrameEventType.ITEM_UNDO:
                itemEvents.pop()
                inventories[participant] = stack.pop()
            else:
                itemId = itemEvent['itemId']
                allEvents = [ItemBuy(item,
                                     eventtype,
                                     game.participantToChamp[participant],
                                     game.mapId,
                                     game.queueType,
                                     game.participantToElo[participant],
                                     goldDiff,
                                     timeStamp,
                                     winningTeam) for item in buyItem(inv, itemId)]
                itemEvents.append(allEvents)
                stack.append(copy(inv))
    return itemEvents
