"""新发田联队"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, DamageType, Event, EventType, Procedure, Rarity, Zone


def enemy_order(card: Card, event: Event, ground: BattleGround) -> bool:
    """敌方使用指令时"""
    return (
        card.zone is Zone.BOARD
        and event.card is not None
        and event.card.type is CardType.ORDER
        and event.player is card.controller.opponent
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对敌方总部造成 1 点伤害"""
    ground.damage(ground.hqs[card.controller.opponent], 1, card, DamageType.NONE)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.JAPAN,
    cost=1,
    display_name="新发田联队",
    text="敌方使用指令时，对其总部造成 1 点伤害。",
    art="shibata_regiment.png",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    procedures=[Procedure(EventType.USE, enemy_order, action)],
)
