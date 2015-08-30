from enum import Enum

class QueueType(Enum):
    """Wrapper for the queue-types that can be returned by the API
    """
    ANY = 'ANY'
    CUSTOM = 'CUSTOM'
    NORMAL_5x5_BLIND = 'NORMAL_5x5_BLIND'
    RANKED_SOLO_5x5 = 'RANKED_SOLO_5x5'
    RANKED_PREMADE_5x5 = 'RANKED_PREMADE_5x5'
    BOT_5x5 = 'BOT_5x5'
    NORMAL_3x3 = 'NORMAL_3x3'
    RANKED_PREMADE_3x3 = 'RANKED_PREMADE_3x3'
    NORMAL_5x5_DRAFT = 'NORMAL_5x5_DRAFT'
    ODIN_5x5_BLIND = 'ODIN_5x5_BLIND'
    ODIN_5x5_DRAFT = 'ODIN_5x5_DRAFT'
    BOT_ODIN_5x5 = 'BOT_ODIN_5x5'
    BOT_5x5_INTRO = 'BOT_5x5_INTRO'
    BOT_5x5_BEGINNER = 'BOT_5x5_BEGINNER'
    BOT_5x5_INTERMEDIATE = 'BOT_5x5_INTERMEDIATE'
    RANKED_TEAM_3x3 = 'RANKED_TEAM_3x3'
    RANKED_TEAM_5x5 = 'RANKED_TEAM_5x5'
    BOT_TT_3x3 = 'BOT_TT_3x3'
    GROUP_FINDER_5x5 = 'GROUP_FINDER_5x5'
    ARAM_5x5 = 'ARAM_5x5'
    ONEFORALL_5x5 = 'ONEFORALL_5x5'
    FIRSTBLOOD_1x1 = 'FIRSTBLOOD_1x1'
    FIRSTBLOOD_2x2 = 'FIRSTBLOOD_2x2'
    SR_6x6 = 'SR_6x6'
    URF_5x5 = 'URF_5x5'
    ONEFORALL_MIRRORMODE_5x5 = 'ONEFORALL_MIRRORMODE_5x5'
    BOT_URF_5x5 = 'BOT_URF_5x5'
    NIGHTMARE_BOT_5x5_RANK1 = 'NIGHTMARE_BOT_5x5_RANK1'
    NIGHTMARE_BOT_5x5_RANK2 = 'NIGHTMARE_BOT_5x5_RANK2'
    NIGHTMARE_BOT_5x5_RANK5 = 'NIGHTMARE_BOT_5x5_RANK5'
    ASCENSION_5x5 = 'ASCENSION_5x5'
    HEXAKILL = 'HEXAKILL'
    BILGEWATER_ARAM_5x5 = 'BILGEWATER_ARAM_5x5'
    KING_PORO_5x5 = 'KING_PORO_5x5'
    COUNTER_PICK = 'COUNTER_PICK'
    BILGEWATER_5x5 = 'BILGEWATER_5x5'

queueTypes = {x for x in QueueType if not x == QueueType.ANY}
rankedQueues = {x for x in {QueueType.RANKED_PREMADE_3x3, QueueType.RANKED_PREMADE_5x5, QueueType.RANKED_SOLO_5x5, QueueType.RANKED_TEAM_3x3, QueueType.RANKED_TEAM_5x5}}

class EloType(Enum):
    """All elo tiers. ANY stands for "unknown, but ranked".
    """
    ANY = 'ANY'
    CHALLENGER = 'CHALLENGER'
    MASTER = 'MASTER'
    DIAMOND = 'DIAMOND'
    PLATINUM = 'PLATINUM'
    GOLD = 'GOLD'
    SILVER = 'SILVER'
    BRONZE = 'BRONZE'
    UNRANKED = 'UNRANKED'

eloTypes = {x for x in EloType if not x == EloType.ANY}

class FrameEventType(Enum):
    """Wrapper for FrameEventTypes as returned by the API
    """
    ASCENDED_EVENT = 'ASCENDED_EVENT'
    BUILDING_KILL = 'BUILDING_KILL'
    CAPTURE_POINT = 'CAPTURE_POINT'
    CHAMPION_KILL = 'CHAMPION_KILL'
    ELITE_MONSTER_KILL = 'ELITE_MONSTER_KILL'
    ITEM_DESTROYED = 'ITEM_DESTROYED'
    ITEM_PURCHASED = 'ITEM_PURCHASED'
    ITEM_SOLD = 'ITEM_SOLD'
    ITEM_UNDO = 'ITEM_UNDO'
    PORO_KING_SUMMON = 'PORO_KING_SUMMON'
    SKILL_LEVEL_UP = 'SKILL_LEVEL_UP'
    WARD_KILL = 'WARD_KILL'
    WARD_PLACED = 'WARD_PLACED'

frameEventTypes = {x for x in FrameEventType}
itemEventTypes = {x for x in {FrameEventType.ITEM_DESTROYED, FrameEventType.ITEM_PURCHASED, FrameEventType.ITEM_SOLD, FrameEventType.ITEM_UNDO}}

class LaneTypes(Enum):
    """Wrapper for Lane specifications as returned by the API
    """
    ANY = 'ANY'
    MID = 'MID'
    MIDDLE = 'MIDDLE'
    TOP = 'TOP'
    JUNGLE = 'JUNGLE'
    BOT = 'BOT'
    BOTTOM = 'BOTTOM'

laneTypes = {x for x in LaneTypes if not x == LaneTypes.ANY}

class RoleTypes(Enum):
    """Wrapper for role specifications as returned by the API
    """
    ANY = 'ANY'
    DUO = 'DUO'
    NONE = 'NONE'
    SOLO = 'SOLO'
    DUO_CARRY = 'DUO_CARRY'
    DUO_SUPPORT = 'DUO_SUPPORT'
    
roleTypes = {x for x in RoleTypes if not x == RoleTypes.ANY}

class Versions(Enum):
    '''Enum wrapper for version
    '''
    ANY = 'ANY'
    v5_14_1 = '5.14.1'
    v5_11_1 = '5.11.1'

versions = {x for x in Versions if not x == Versions.ANY}

def getVersionEnum(longversion):
    for version in Versions:
        if longversion.startswith(version.value): return version
    return Versions.ANY

class RegionTypes(Enum):
    '''Enum wrapper for regions
    '''
    ANY = 'ANY',
    EUW = 'EUW',
    KR = 'KR',
    RU = 'RU',
    TR = 'TR',
    BR = 'BR',
    EUNE = 'EUNE',
    LAN = 'LAN',
    LAS = 'LAS',
    NA = 'NA',
    OCE = 'OCE'

regions = {x for x in RegionTypes if not x == RegionTypes.ANY}

relevantVersions = {"5.14.1", "5.11.1"}
availableMaps = {x for x in range(11)}
