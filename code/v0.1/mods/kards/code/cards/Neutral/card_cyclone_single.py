"""旋风"""
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
    LineKind,
    Rarity,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 任意单位"""
    return target.is_unit


def adjacent_targets(target: Card, ground: BattleGround) -> list[Card]:
    """返回与目标相邻的单位和 HQ"""
    line = target.line
    if line is None or target not in line.units:
        return []
    index = line.units.index(target)
    result: list[Card] = []
    if index > 0:
        result.append(line.units[index - 1])
    if index + 1 < len(line.units):
        result.append(line.units[index + 1])
    if line.kind is LineKind.SUPPORT and line.owner is not None:
        position = index if index < line.hq_index else index + 1
        if abs(position - line.hq_index) == 1:
            result.append(ground.hqs[line.owner])
    return result


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对目标和相邻目标造成伤害"""
    player = event.player

    def apply(target: Card) -> None:
        neighbors = adjacent_targets(target, ground)
        ground.damage(target, 6, card, DamageType.NONE)
        for neighbor in neighbors:
            ground.damage(neighbor, 2, card, DamageType.NONE)

    ground.request_target(player, card, lambda target: target_valid(target, player, ground), apply)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="旋风",
    text="对一个单位造成 6 点伤害，对其相邻目标（含 HQ）造成 2 点伤害。。",
    art="cyclone_single.png",
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
