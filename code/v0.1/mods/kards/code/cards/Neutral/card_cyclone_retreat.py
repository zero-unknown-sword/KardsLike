"""旋风 (撤退)"""
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
    Zone,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有单位撤退"""
    for unit in list(ground.all_targets()):
        if unit.is_unit and unit.zone is Zone.BOARD:
            ground.retreat_unit(unit, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="旋风",
    text="所有单位撤退。预报。",
    art="cyclone.png",
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
