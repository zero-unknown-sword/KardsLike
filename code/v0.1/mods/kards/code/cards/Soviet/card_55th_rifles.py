"""步兵第 55 团"""
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
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def destroyed(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身被消灭时触发"""
    return (
        event.dict.get("card") is card
        and event.dict.get("way") == LeaveMethod.DESTROYED
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """下个友方回合开始时获得 3K"""
    player = card.controller

    def grant() -> None:
        ground.kredits[player].credits += 3

    ground.start_shadow_timer(player, grant)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="步兵第 55 团",
    text="守护。亡计：下个友方回合开始时，获得 3K。",
    art="55th_rifles.png",
    rare=Rarity.LIMITED,
    at=3,
    df=4,
    operation_cost=1,
    keywords=[GUARD],
    procedures=[Procedure(EventType.LEAVE, destroyed, action)],
)
