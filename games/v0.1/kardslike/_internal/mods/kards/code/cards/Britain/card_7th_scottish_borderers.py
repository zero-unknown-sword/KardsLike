"""苏格兰边民团第 7 营"""
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
    DamageType,
    Event,
    EventType,
    Procedure,
)


def intel_overflow(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    条件: 友方产生情报溢出

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return event.dict.get("player") is card.controller


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    每溢出 1 情报, 对敌方总部造成 1 点伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    if card.controller is None:
        return
    amount = event.dict.get("amount", 0)
    if isinstance(amount, int) and amount > 0:
        ground.damage(
            ground.hqs[card.controller.opponent],
            amount,
            DamageType.NONE,
            card,
        )


from mods.kards.code.keywords.smoke import KEYWORD as SMOKE
from mods.kards.code.keywords.intel import KEYWORD as INTEL

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=2,
    display_name="苏格兰边民团第 7 营",
    text="烟幕。情报 3。每溢出 1 情报，对敌方总部造成 1 点伤害。",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    keywords=[SMOKE, INTEL.with_val(3)],
    procedures=[Procedure(EventType.INTEL_OVERFLOW, intel_overflow, action)],
)
