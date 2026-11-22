"""骄阳"""
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
    EntryMethod,
    Event,
    EventType,
    Player,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.pfwd import KEYWORD as PFWD
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import add_end_cleanup, add_turn_hook, start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有友方单位 +3 +2"""
    player = event.player
    for unit in ground.all_targets():
        if unit.is_unit and unit.controller is player:
            ground.buff(unit, at=3, df=2)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="骄阳",
    text="所有友方单位 +3 攻击力，+2 防御力。预报。",
    art="scorching_sun.png",
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
