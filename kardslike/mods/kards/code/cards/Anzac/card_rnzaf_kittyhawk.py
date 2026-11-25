"""RNZAF 小鹰"""
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
    EntryMethod
)


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    条件: 有单位部署

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    unit = event.dict.get("card")
    return isinstance(unit, Card) and unit.is_unit and event.method == EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    敌方总部受到 1 点伤害, 友方总部 +1 防御力

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    enemy_hq = ground.hqs[card.controller.opponent]
    ally_hq = ground.hqs[card.controller]
    ground.damage(enemy_hq, 1, card, DamageType.NONE)
    ally_hq.buff(df=1)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.ANZAC,
    cost=5,
    display_name="RNZAF 小鹰",
    text="单位部署时，对敌方总部造成 1 点伤害，使友方总部获得 +1 防御力。",
    rare=Rarity.SPECIAL,
    at=3,
    df=4,
    operation_cost=2,
    procedures=[Procedure(EventType.ENTER, deployed, action)],
)
