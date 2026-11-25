"""金泽联队"""
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
    LeaveMethod,
    Procedure,
    Rarity,
    Zone,
)


def left_without_destruction(card: Card, event: Event, ground: BattleGround) -> bool:
    """其他单位不因消灭离开战场时"""
    return (
        card.zone is Zone.BOARD
        and event.card is not card
        and event.dict.get("way") is not LeaveMethod.DESTROYED
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对敌方总部造成 2 点伤害, 使友方总部获得 +2 防御力"""
    player = card.controller
    ground.damage(ground.hqs[player.opponent], 2, card, DamageType.NONE)
    ground.buff(ground.hqs[player], df=2)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.JAPAN,
    cost=5,
    display_name="金泽联队",
    text="单位不因消灭离开战场时，对敌方总部造成 2 点伤害，使友方总部获得 +2 防御力。",
    art="kanazawa_regiment.png",
    rare=Rarity.LIMITED,
    at=5,
    df=5,
    operation_cost=1,
    procedures=[Procedure(EventType.LEAVE, left_without_destruction, action)],
)
