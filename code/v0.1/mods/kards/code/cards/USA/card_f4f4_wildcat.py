"""F4F-4 野猫"""
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
    LineKind,
    Procedure,
    cards,
)


def moved_to_front(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    条件: 本单位移动到前线

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return (
        event.dict.get("card") is card
        and card.line is not None
        and card.line.kind is LineKind.FRONT
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    将 1 个 F2A 水牛加入相邻处

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    line = card.line
    if line is None:
        return
    index = line.units.index(card)
    insert_at = index + 1
    token = cards.create("kards:card_brewster_f2a")
    ground.add_unit(card.controller, token, line=line, index=insert_at)


from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

from main import Rarity

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.USA,
    cost=2,
    display_name="F4F-4 野猫",
    text="闪击。移至前线时，将 1 个“F2A 水牛”加入相邻处。",
    rare=Rarity.SPECIAL,
    at=2,
    df=3,
    operation_cost=2,
    keywords=[BLITZ],
    procedures=[Procedure(EventType.MOVE, moved_to_front, action)],
)
