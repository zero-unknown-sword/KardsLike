"""步兵第 75 团"""
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
    Procedure,
    Rarity,
    cards,
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def targeted_by_enemy(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    是否被敌方效果指向

    Args:
        card: 自身
        event: TARGETED 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return (
        event.dict.get("target") is card
        and event.dict.get("player") is not card.controller
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    在被指向时, 将 1 个复制加入友方 HQ 相邻处

    Args:
        card: 自身
        event: TARGETED 事件
        ground: 战斗全局参数
    """
    player = card.controller
    line = ground.support_lines[player]
    copy = cards.create(card.card_id)
    ground.add_unit(
        player,
        copy,
        index=line.hq_index + 1,
        line=line,
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=6,
    display_name="步兵第 75 团",
    text="守护。被敌方效果指向时，将 1 个复制加入友方总部相邻处。",
    art="75th_rifle_regiment.png",
    rare=Rarity.ELITE,
    at=6,
    df=7,
    operation_cost=2,
    keywords=[GUARD],
    procedures=[
        Procedure(
            EventType.TARGETED,
            targeted_by_enemy,
            action,
        )
    ],
)
