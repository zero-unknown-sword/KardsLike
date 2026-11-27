"""达努塔装甲列车"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone
from mods.kards.code.keywords.armor import KEYWORD as ARMOR
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.POLAND,
    cost=3,
    display_name="达努塔装甲列车",
    text="守护。重甲 1。友方回合开始时召集 4TP，回合结束时消灭 4TP。",
    art="danuta.png",
    rare=Rarity.LIMITED,
    at=3,
    df=3,
    operation_cost=4,
    keywords=[GUARD, ARMOR.with_val(1)],
    procedures=[
        Procedure(
            EventType.TURN_START,
            lambda card, event, ground: event.player is card.controller and card.zone is Zone.BOARD,
            lambda card, event, ground: setattr(
                card,
                "summoned_4tp",
                ground.give_card(card.controller, "kards:card_4tp", Zone.BOARD),
            ),
        ),
        Procedure(
            EventType.TURN_END,
            lambda card, event, ground: getattr(card, "summoned_4tp", None) is not None,
            lambda card, event, ground: _remove_4tp(card, ground),
        ),
    ],
)

def _remove_4tp(card, ground):
    unit = getattr(card, "summoned_4tp", None)
    if unit is not None and unit.zone is Zone.BOARD:
        ground.kill(unit, source=card)
    card.summoned_4tp = None
