import pickle
from enum import Enum
from lolstatic import EloType, Items, ItemEventTypes, FrameEventType, QueueType,\
    RoleTypes, LaneTypes
from collections import defaultdict, namedtuple
from functools import partial
from copy import copy
from .Sections import getGoldSection, getTimeSection
from .InventoryHandler import Inventory
from riotapi import AnswerException, getDownloader

def loadGame(region, gameID):
    """Loads and parses a game into the then stored data format:
    For every item that is bought in the game and not undone, keep an entry and store whether that game was won or lost
    @param region: the region the game took place in
    @param gameID: the id of the game to load
    @return: a Game object that contains data about the game
    """
    dl = getDownloader(region)
    gameAnswer = dl.api_request('/api/lol/{region}/v2.2/match/{matchId}'.format(region = region, matchId = gameID), _reg = region, includeTimeline = True)
    #with open("../data/raw/games/{region}_{id}.pkl".format(region = region, id = gameID) , 'wb') as file:
    #    pickle.dump(gameAnswer, file)
    return Game(gameAnswer)

class Winner(Enum):
    """Aliases for the winner. Yes, Blue is the good team
    """
    Blue = True
    Red = False

ItemBuy = namedtuple("ItemBuy", "itemId eventType champion mapId queueType participantElo role lane goldDiff timeStamp winner")

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
        self.participants = json['participants']
        self.participantToTeam = {part['participantId']: part['teamId'] for part in json['participants']}
        self.participantToChamp = {part['participantId']: part['championId'] for part in json['participants']}
        self.participantToElo = defaultdict(lambda: EloType.ANY)
        self.summonerIdToParticipant = defaultdict(lambda:0)
        self.summonerIdToParticipant.update({p['player']['summonerId']:p['participantId'] for p in json['participantIdentities'] if 'player' in p})
        dl = getDownloader(self.region.lower())
        if self.summonerIdToParticipant:
            try:
                ans = dl.api_request("/api/lol/{region}/v2.5/league/by-summoner/{summonerId}/entry".format(region = self.region.lower(),
                        summonerId = ",".join(str(p) for p in self.summonerIdToParticipant)), _reg = self.region.lower())
                summonerToRanking = {summonerId:defaultdict(lambda:EloType.UNRANKED, {QueueType(ranking['queue']):EloType(ranking['tier']) for ranking in ans[str(summonerId)]} 
                                                                                        if str(summonerId) in ans else dict()) 
                                    for summonerId in self.summonerIdToParticipant}
                self.participantToElo.update({self.summonerIdToParticipant[summId]: summonerToRanking[summId][self.queueType] for summId in self.summonerIdToParticipant})
            except AnswerException as e:
                if e.answer.status != 404:
                    raise
                self.participantToElo.update({self.summonerIdToParticipant[summonerId]:EloType.UNRANKED for summonerId in self.summonerIdToParticipant})

def item_events(game):
    """
    Analyses a whole game, going through the timeline frame by frame, and extracts information about items.
    It returns a list of all item related action that where not undone in the shop directly afterwards.
    Each action features certain stats, see the class ItemBuy for a list of those.
    @param game: the game to analyze
    @return: a list of ItemBuy actions
    """
    itemEvents = []
    inventoryStacks = defaultdict(list)
    inventories = defaultdict(Inventory)
    gold = defaultdict(int)
    role = defaultdict(lambda:RoleTypes.NONE)
    lane = defaultdict(lambda:LaneTypes.JUNGLE)
    role.update({part['participantId']:RoleTypes(part['timeline']['role']) for part in game.participants})
    lane.update({part['participantId']:LaneTypes(part['timeline']['lane']) for part in game.participants})
    for frame in game.timeline:
        gold[game.teamBlueId] = 0
        gold[game.teamRedId] = 0
        for player in frame['participantFrames']:
            goldInc = frame['participantFrames'][player]['totalGold']
            gold[game.participantToTeam[int(player)]] += goldInc
        if 'events' not in frame:
            continue
        allEvents = sorted(frame['events'], key = lambda ev: ev['timestamp'])
        for itemEvent in filter(lambda x: x['eventType'] in ItemEventTypes and x['participantId'], frame['events']):
            participant = itemEvent['participantId']
            inv = inventories[participant]
            stack = inventoryStacks[participant]
            eventtype = FrameEventType(itemEvent['eventType'])
            teamId = game.participantToTeam[participant]
            winningTeam = Winner(game.winner == teamId)
            goldDiff = gold[game.teamBlueId]-gold[game.teamRedId] * ( -1 if teamId == game.teamBlueId else 1)
            timeStamp = itemEvent['timestamp']
            
            if eventtype == FrameEventType.ITEM_DESTROYED:
                itemId = itemEvent['itemId']
                itemEvents.append([ItemBuy(itemId,
                                           eventtype,
                                           game.participantToChamp[participant],
                                           game.mapId,
                                           game.queueType,
                                           game.participantToElo[participant],
                                           role[participant],
                                           lane[participant],
                                           goldDiff,
                                           timeStamp,
                                           winningTeam)])
                stack.append(copy(inv))
                inv.removeItem(itemId)
            elif eventtype == FrameEventType.ITEM_SOLD:
                itemId = itemEvent['itemId']
                itemEvents.append([ItemBuy(itemId,
                                           eventtype,
                                           game.participantToChamp[participant],
                                           game.mapId,
                                           game.queueType,
                                           game.participantToElo[participant],
                                           role[participant],
                                           lane[participant],
                                           goldDiff,
                                           timeStamp,
                                           winningTeam)])
                stack.append(copy(inv))
                inv.removeItem(itemId)
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
                                     role[participant],
                                     lane[participant],
                                     goldDiff,
                                     timeStamp,
                                     winningTeam) for item in inv.buyItem(itemId)]
                itemEvents.append(allEvents)
                stack.append(copy(inv))
    
    return [e for l in itemEvents for e in l]
