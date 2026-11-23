"""斯大林管风琴"""
import random
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
    Rarity,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """将 8 点伤害随机分配给所有敌方目标"""
    player = event.player
    targets = [
        item
        for item in ground.all_targets()
        if item.controller is not player
    ]
    for _ in range(8):
        if not targets:
            break
        ground.damage(random.choice(targets), 1, card, DamageType.NONE)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=4,
    display_name="斯大林管风琴",
    text="造成 8 点伤害，随机分配至所有敌方目标。",
    art="stalins_organ.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
