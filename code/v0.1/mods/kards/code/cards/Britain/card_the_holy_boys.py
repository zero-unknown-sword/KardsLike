"""神圣男孩步兵团"""
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
    Event,
    EventType,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def neutral_used(card: Card, event: Event, ground: BattleGround) -> bool:
    """本回合第一次友方使用中立牌"""
    used = event.card
    return (
        card.zone is Zone.BOARD
        and event.player is card.controller
        and used.country is Country.NEUTRAL
        and card.last_trigger_turn != ground.turn_count
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有友方单位 +1+1"""
    card.last_trigger_turn = ground.turn_count
    for unit in ground.units_in_effect_order(card.controller):
        if unit.controller is card.controller:
            ground.buff(unit, at=1, df=1)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=4,
    display_name="神圣男孩步兵团",
    text="守护。一回合一次，友方使用中立牌时，所有友方单位 +1+1。",
    art="the_holy_boys.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=5,
    operation_cost=1,
    keywords=[GUARD],
    procedures=[Procedure(EventType.USE, neutral_used, action)],
)
