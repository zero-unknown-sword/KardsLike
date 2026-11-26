"""STZ-5 喀秋莎"""
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
    Zone,
    DamageType,
)


def dealt_damage(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身造成对战伤害时触发。"""
    return (
        event.dict.get("source") is card
        and event.dict.get("target") is not card
        and event.dict.get("kind") in (DamageType.COUNTER, DamageType.ATTACK)
        and int(event.dict.get("amount", 0)) > 0
    )


def add_blast(card: Card, event: Event, ground: BattleGround) -> None:
    """按伤害量把爆破加入手牌。"""
    amount = int(event.dict.get("amount", 0))
    for _ in range(amount):
        ground.give_card(card.controller, "kards:card_blast", Zone.HAND)


CARD_DATA = CardData(
    type=CardType.ARTILLERY,
    country=Country.SOVIET,
    cost=3,
    display_name="STZ-5 喀秋莎",
    text="本单位造成对战伤害时，将等量的“爆破”加入手中。",
    art="stz5_katyusha.png",
    rare=Rarity.SPECIAL,
    at=1,
    df=2,
    operation_cost=0,
    procedures=[
        Procedure(EventType.DAMAGED, dealt_damage, add_blast),
    ],
)
