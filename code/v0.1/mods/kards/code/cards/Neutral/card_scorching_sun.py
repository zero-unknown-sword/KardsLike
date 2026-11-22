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
from mods.kards.code.keywords.pfwd import KEYWORD as PFWD
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """将手中所有单位加入战场并压制"""
    player = event.player
    units = [item for item in list(ground.hands[player].cards) if item.is_unit]
    for unit in units:
        if ground.add_unit(player, unit):
            ground.suppress(unit)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="骄阳",
    text="将手中所有单位加入战场，将其压制直到回合结束。预报。",
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
