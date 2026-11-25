"""HX 175 护航队"""
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
    """抽 2 张牌"""
    for _ in range(2):
        ground.draw(event.player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.BRITAIN,
    cost=3,
    display_name="HX 175 护航队",
    text="抽 2 张牌。",
    art="convoy_hx_175.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
