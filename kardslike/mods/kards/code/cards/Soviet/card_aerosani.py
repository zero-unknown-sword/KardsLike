"""气动雪橇"""
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
    LineKind,
    Player,
    Procedure,
    Rarity,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 敌方陆军或总部"""
    return (
        target.controller is not player
        and (target.is_hq or target.type in (CardType.INFANTRY, CardType.ARTILLERY, CardType.TANK))
    )


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
    """对目标及相邻目标各造成 2 点伤害"""
    player = event.player

    def apply(target: Card) -> None:
        neighbors = adjacent_targets(target, ground)
        ground.damage(target, 2, card, DamageType.NONE)
        for neighbor in neighbors:
            ground.damage(neighbor, 2, card, DamageType.NONE)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=0,
    display_name="气动雪橇",
    text="对 1 个敌方陆军或总部造成 2 点伤害，对其相邻目标造成 2 点伤害。",
    art="aerosani.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
