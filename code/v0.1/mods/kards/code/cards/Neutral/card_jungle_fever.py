"""丛林热"""
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
    """所有单位 +3 攻击力, 压制未攻击的友方单位"""
    player = event.player
    for unit in ground.all_targets():
        if not unit.is_unit:
            continue
        unit.add_temporary_at(3)
        if unit.controller is player and unit.attacks_turn == 0:
            ground.suppress(unit)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="丛林热",
    text="所有单位 +3 攻击力，压制未攻击的友方单位。预报。",
    art="jungle_fever.png",
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
