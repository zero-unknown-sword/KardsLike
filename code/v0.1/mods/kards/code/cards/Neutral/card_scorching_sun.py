"""骄阳"""
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
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """将手中所有单位加入战场并压制"""
    player = event.player
    units = [item for item in list(ground.hands[player].cards) if item.is_unit]
    for unit in units:
        if ground.add_unit(player, unit):
            ground.suppress(unit, until_turn_end=True)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="骄阳",
    text="将手中所有单位加入战场，将其压制直到回合结束。",
    art="scorching_sun.png",
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
