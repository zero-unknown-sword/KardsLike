"""严冬"""
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
    Line,
    Player,
    Procedure,
    cards,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    移除所有单位, 并按相同数量把轻步兵加入原来的阵线

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    units: list[tuple[Card, Player, Line]] = []
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in list(line.units):
            units.append((unit, unit.controller, line))
    for unit, _, _ in units:
        card.remove(unit, ground)

    def add_tokens() -> None:
        for _, player, line in units:
            token = cards.create("kards:card_light_infantry")
            ground.add_unit(player, token, line=line)

    ground.schedule_action(900, add_tokens)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=5,
    display_name="严冬",
    text="移除所有单位。将等量“轻步兵”加入同一阵线。",
    rare=Rarity.ELITE,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
