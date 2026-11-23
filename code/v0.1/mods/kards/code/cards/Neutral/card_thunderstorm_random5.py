"""雷暴"""
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
    Player,
    Procedure,
    Rarity,
)
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """随机对一个敌方单位造成 5 点伤害"""
    player = event.player
    targets = [
        item
        for item in ground.all_targets()
        if item.is_unit and item.controller is not player
    ]
    if targets:
        ground.damage(random.choice(targets), 5, card, DamageType.NONE)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="雷暴",
    text="随机对 1 个敌方单位造成 5 点伤害。",
    art="thunderstorm_random5.png",
    rare=Rarity.STANDARD,
    sub_type="weather",
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
