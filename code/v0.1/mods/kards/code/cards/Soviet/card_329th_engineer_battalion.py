"""工兵第 329 营"""
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
)


def other_friendly_destroyed(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    条件: 另一个友方单位被消灭

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    victim = event.dict.get("card")
    return (
        isinstance(victim, Card)
        and victim is not card
        and event.dict.get("way") == LeaveMethod.DESTROYED
        and victim.controller is card.controller
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    使友方总部获得 +2 防御力

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    if card.controller is not None:
        ground.buff(ground.hqs[card.controller], df=2)


from mods.kards.code.keywords.smoke import KEYWORD as SMOKE

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="工兵第 329 营",
    text="烟幕。其他友方单位被消灭时，使友方总部获得 +2 防御力。",
    rare=Rarity.STANDARD,
    at=0,
    df=4,
    operation_cost=4,
    keywords=[SMOKE],
    procedures=[Procedure(EventType.LEAVE, other_friendly_destroyed, action)],
)
