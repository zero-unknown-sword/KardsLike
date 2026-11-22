"""雷暴"""
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
    Zone,
)
import random
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """3 点伤害随机分配给敌方目标"""
    player = event.player
    targets = [
        item
        for item in ground.all_targets()
        if item.controller is not player or item.is_hq and item is ground.hqs[player.opponent]
    ]
    if not targets:
        return
    for _ in range(3):
        ground.damage(random.choice(targets), 1, card, DamageType.NONE)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="雷暴",
    text="造成 3 点伤害，随机分配至所有敌方目标。预报。",
    art="thunderstorm.png",
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
