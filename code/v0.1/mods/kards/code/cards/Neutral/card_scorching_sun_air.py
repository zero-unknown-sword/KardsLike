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
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import add_end_cleanup, add_turn_hook, start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """本回合友方空军 OC=0 且攻击时伤害敌方总部"""
    player = event.player
    old_cost: dict[int, int] = {}
    air_types = (CardType.FIGHTER, CardType.BOMBER)
    for unit in ground.all_targets():
        if unit.is_unit and unit.controller is player and unit.type in air_types:
            old_cost[id(unit)] = unit.operation_cost
            unit.operation_cost = 0

    def on_attack(event: Event, ground: BattleGround) -> None:
        attacker = event.dict.get("card")
        if not isinstance(attacker, Card):
            return
        if attacker.controller is not player or attacker.type not in air_types:
            return
        ground.damage(
            ground.hqs[player.opponent],
            attacker.at,
            attacker,
            DamageType.NONE,
        )

    def cleanup() -> None:
        for unit in ground.all_targets():
            if unit.is_unit and id(unit) in old_cost:
                unit.operation_cost = old_cost[id(unit)]

    add_turn_hook(ground, player, EventType.ATTACK, on_attack, cleanup)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="骄阳",
    text="本回合，所有友方空军行动花费为 0，攻击时也对敌方总部造成伤害。预报。",
    art="scorching_sun_air.png",
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
