"""同盟国"""
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
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    所有友方非美国单位获得 +2+2

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in line.units:
            if unit.controller is player and unit.country is not Country.USA:
                ground.buff(unit, at=2, df=2)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=5,
    display_name="同盟国",
    text="使所有友方非美国单位获得 +2+2。",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
