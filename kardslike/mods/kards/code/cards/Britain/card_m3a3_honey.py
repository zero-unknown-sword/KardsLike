"""M3A3 甜心"""
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


def friendly_drew(card: Card, event: Event, ground: BattleGround) -> bool:
    """友方抽牌"""
    return event.player is card.controller


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """友方总部 +1 防御力"""
    ground.buff(ground.hqs[card.controller], df=1)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.BRITAIN,
    cost=2,
    display_name="M3A3 甜心",
    text="友方每抽 1 张牌，友方总部 +1 防御力。",
    art="m3a3_honey.png",
    rare=Rarity.LIMITED,
    at=2,
    df=3,
    operation_cost=1,
    procedures=[Procedure(EventType.DRAW, friendly_drew, action)],
)
