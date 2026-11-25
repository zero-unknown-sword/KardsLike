"""IS-2"""
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
    cards,
)
from mods.kards.code.keywords.armor import KEYWORD as ARMOR


def returned(card: Card, event: Event, ground: BattleGround) -> bool:
    """被返回手牌时触发"""
    return (
        event.dict.get("card") is card
        and event.dict.get("way") is LeaveMethod.RETURN_HAND
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """召集 1 个复制到支援阵线"""
    copy = cards.create(card.card_id)
    ground.add_unit(card.controller, copy)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.SOVIET,
    cost=10,
    display_name="IS-2",
    text="重甲 2。被返回手中时，召集 1 个复制。",
    art="iosef_stalin_ii.png",
    rare=Rarity.ELITE,
    at=8,
    df=8,
    operation_cost=1,
    keywords=[ARMOR.with_val(2)],
    procedures=[Procedure(EventType.LEAVE, returned, action)],
)
