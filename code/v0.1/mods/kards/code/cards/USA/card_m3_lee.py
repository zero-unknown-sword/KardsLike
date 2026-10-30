"""M3 李"""
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
    使卡组中所有单位获得 +1 攻击力

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    for item in ground.decks[card.controller].cards:
        if item.is_unit:
            item.apply_permanent(at=1)


from mods.kards.code.keywords.bond import KEYWORD as BOND
from mods.kards.code.keywords.smoke import KEYWORD as SMOKE
from mods.kards.code.keywords.ambush import KEYWORD as AMBUSH

from main import Rarity

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.USA,
    cost=3,
    display_name="M3 李",
    text="协力。烟幕。伏击。移至前线时，卡组中所有单位获得 +1 攻击力。",
    rare=Rarity.SPECIAL,
    at=4,
    df=4,
    operation_cost=2,
    keywords=[BOND, SMOKE, AMBUSH],
    procedures=[Procedure(EventType.MOVE, moved_to_front, action)],
)
