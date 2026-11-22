"""热浪"""
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
    """本回合友方部署时对随机敌人造成自身攻击力伤害"""
    player = event.player

    def on_enter(event: Event, ground: BattleGround) -> None:
        unit = event.dict.get("card")
        if not isinstance(unit, Card):
            return
        if event.dict.get("method") is not EntryMethod.DEPLOY:
            return
        if not unit.is_unit or unit.controller is not player:
            return
        targets = [
            item
            for item in ground.all_targets()
            if item.controller is not player
        ]
        if targets:
            ground.damage(random.choice(targets), unit.at, unit, DamageType.NONE)

    add_turn_hook(ground, player, EventType.ENTER, on_enter)
    start_climate_choice(ground, player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="热浪",
    text="本回合，友方单位部署时，随机对一个敌方目标造成等同于自身攻击力的伤害。预报。",
    art="heatwave.png",
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
