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

queueTypes = {x.value for x in QueueType}
rankedQueues = {x.value for x in {QueueType.RANKED_PREMADE_3x3, QueueType.RANKED_PREMADE_5x5, QueueType.RANKED_SOLO_5x5, QueueType.RANKED_TEAM_3x3, QueueType.RANKED_TEAM_5x5}}

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

eloTypes = {x.value for x in EloType}

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

frameEventTypes = {x.value for x in FrameEventType}
ItemEventTypes = {x.value for x in {FrameEventType.ITEM_DESTROYED, FrameEventType.ITEM_PURCHASED, FrameEventType.ITEM_SOLD, FrameEventType.ITEM_UNDO}}

class LaneTypes(Enum):
    """Wrapper for Lane specifications as returned by the API
    """
    MID = 'MID'
    MIDDLE = 'MIDDLE'
    TOP = 'TOP'
    JUNGLE = 'JUNGLE'
    BOT = 'BOT'
    BOTTOM = 'BOTTOM'
    
class RoleTypes(Enum):
    """Wrapper for role specifications as returned by the API
    """
    DUO = 'DUO'
    NONE = 'NONE'
    SOLO = 'SOLO'
    DUO_CARRY = 'DUO_CARRY'
    DUO_SUPPORT = 'DUO_SUPPORT'
    
relevantVersions = {"5.14.1", "5.11.1"}
