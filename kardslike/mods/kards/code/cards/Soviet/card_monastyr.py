"""修道院行动"""
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
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """消灭所有对战词条数不大于 1 的单位。"""
    for unit in list(ground.all_targets()):
        if unit.is_unit and len(unit.keywords) <= 1:
            card.destroy(unit, ground)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=8,
    display_name="修道院行动",
    text="消灭所有对战词条数不大于 1 的单位。",
    art="monastyr.png",
    rare=Rarity.ELITE,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
