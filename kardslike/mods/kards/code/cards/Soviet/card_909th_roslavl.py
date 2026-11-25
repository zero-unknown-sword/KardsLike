"""罗斯拉夫尔第 909 团"""
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
    Player,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def aura(card: Card, event: Event, ground: BattleGround) -> None:
    """
    友方步兵获得闪击

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in line.units:
            if unit.controller is card.controller and unit.type is CardType.INFANTRY:
                ground.add_aura(unit, keyword="blitz", source=card)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=5,
    display_name="罗斯拉夫尔第 909 团",
    text="守护。友方步兵具有闪击。",
    art="909th_roslavl.png",
    rare=Rarity.ELITE,
    at=3,
    df=8,
    operation_cost=1,
    keywords=[GUARD],
    procedures=[
        Procedure(EventType.LOOP, lambda card, event, ground: True, aura)
    ],
)
