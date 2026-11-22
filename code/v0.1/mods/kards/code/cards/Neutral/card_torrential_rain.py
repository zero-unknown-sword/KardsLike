"""骤雨"""
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
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """友方步兵和总部 +3 防御力, 其他友方单位 +2 防御力"""
    player = event.player
    ground.buff(ground.hqs[player], df=3)
    for unit in ground.all_targets():
        if not unit.is_unit or unit.controller is not player:
            continue
        ground.buff(unit, df=3 if unit.type is CardType.INFANTRY else 2)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="骤雨",
    text="友方步兵和总部 +3 防御力，其他友方单位 +2 防御力。。",
    art="torrential_rain.png",
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
