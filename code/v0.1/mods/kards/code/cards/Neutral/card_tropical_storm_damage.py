"""热带风暴"""
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
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 任意敌方目标"""
    return target.controller is player.opponent


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """指向 3 点, 再随机 2 点和 1 点"""
    player = event.player

    def apply(target: Card) -> None:
        ground.damage(target, 3, card, DamageType.NONE)
        targets = [
            item
            for item in ground.all_targets()
            if item.is_unit and item.controller is not player
        ]
        if targets:
            ground.damage(random.choice(targets), 2, card, DamageType.NONE)
        targets = [
            item
            for item in ground.all_targets()
            if item.is_unit and item.controller is not player
        ]
        if targets:
            ground.damage(random.choice(targets), 1, card, DamageType.NONE)

    ground.request_target(player, card, lambda target: target_valid(target, player, ground), apply)


def target_valid_placeholder() -> None:
    """占位"""

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="热带风暴",
    text="对一个敌方目标造成 3 点伤害，随机对一个敌方单位造成 2 点伤害，再随机对一个敌方单位造成 1 点伤害。。",
    art="tropical_storm_damage.png",
    rare=Rarity.STANDARD,
    keywords=[WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
