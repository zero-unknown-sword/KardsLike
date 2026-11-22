"""暴雨"""
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
from mods.kards.code.keywords.pfwd import KEYWORD as PFWD
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """6 点防御力随机分配给友方目标"""
    player = event.player
    targets = [
        item
        for item in ground.all_targets()
        if item.controller is player
    ]
    for _ in range(6):
        if not targets:
            break
        ground.buff(random.choice(targets), df=1)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="暴雨",
    text="增加 6 点防御力，随机分配至所有友方目标。预报。",
    art="deluge.png",
    rare=Rarity.STANDARD,
    keywords=[PFWD, WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
