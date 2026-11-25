"""近卫步兵第 178 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardData,
    CardType,
    Country,
    Event,
    EventType,
    LeaveMethod,
    Procedure,
    Rarity,
    Zone,
    cards,
)
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def destroyed(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身被消灭时触发"""
    return (
        event.dict.get("card") is card
        and event.dict.get("way") == LeaveMethod.DESTROYED
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """召集步兵第 89 团"""
    player = card.controller
    token = cards.create("kards:card_89th_infantry_regiment")
    ground.add_unit(player, token)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="近卫步兵第 178 团",
    text="守护。亡计：召集 1 个步兵第 89 团。",
    art="178th_guard_rifles.png",
    rare=Rarity.STANDARD,
    at=1,
    df=4,
    operation_cost=1,
    keywords=[GUARD, DESTRUCTION],
    procedures=[Procedure(EventType.LEAVE, destroyed, action)],
)
