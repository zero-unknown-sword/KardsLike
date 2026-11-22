"""丛林热"""
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
    """本回合友方单位进入时 +2 攻击力和闪击"""
    player = event.player
    boosted: list[Card] = []

    def on_enter(event: Event, ground: BattleGround) -> None:
        unit = event.dict.get("card")
        if not isinstance(unit, Card):
            return
        if not unit.is_unit or unit.controller is not player:
            return
        unit.add_temporary_at(2)
        if not unit.has_keyword("blitz"):
            unit.keywords.append("blitz")
            boosted.append(unit)

    def cleanup() -> None:
        for unit in boosted:
            if "blitz" in unit.keywords:
                unit.keywords.remove("blitz")

    add_turn_hook(ground, player, EventType.ENTER, on_enter, cleanup)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="丛林热",
    text="本回合，友方单位进入时 +2 攻击力并获得闪击。预报。",
    art="jungle_fever.png",
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
