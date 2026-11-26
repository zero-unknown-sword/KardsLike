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
    battle_keywords = {"guard", "ambush", "blitz", "shock", "smoke", "fury", "armor"}
    for unit in list(ground.all_targets()):
        if not unit.is_unit:
            continue
        count = sum(1 for keyword in unit.keywords if keyword in battle_keywords)
        if count <= 2:
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
