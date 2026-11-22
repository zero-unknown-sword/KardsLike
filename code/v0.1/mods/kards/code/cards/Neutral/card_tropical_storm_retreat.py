"""热带风暴"""
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
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """随机撤退一个敌方单位, 再随机消灭一个敌方单位"""
    player = event.player
    targets = [
        item
        for item in ground.all_targets()
        if item.is_unit and item.controller is not player
    ]
    if targets:
        ground.retreat_unit(random.choice(targets), card)
    targets = [
        item
        for item in ground.all_targets()
        if item.is_unit and item.controller is not player
    ]
    if targets:
        ground.kill(random.choice(targets), card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="热带风暴",
    text="随机撤退一个敌方单位，然后随机消灭一个敌方单位。。",
    art="tropical_storm_retreat.png",
    rare=Rarity.STANDARD,
    keywords=[WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
