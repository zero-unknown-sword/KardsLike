"""第 102 掷弹兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone
from mods.kards.code.veteran import VeteranProfile, promote, register_veteran


def acted(card: Card, event: Event, ground: BattleGround) -> bool:
    """本单位行动后"""
    return card.zone is Zone.BOARD and event.dict.get("card") is card


def promote_action(card: Card, event: Event, ground: BattleGround) -> None:
    """升为老兵"""
    promote(card, ground)


MOVE_PROC = Procedure(EventType.MOVE, acted, promote_action)
ATTACK_PROC = Procedure(EventType.ATTACK, acted, promote_action)
BASE_PROCEDURES = [MOVE_PROC, ATTACK_PROC]

VETERAN = VeteranProfile(
    at=2,
    df=3,
    operation_cost=1,
    art="102_grenadier_vet.png",
    text="",
    base_procedures=BASE_PROCEDURES,
)

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=1,
    display_name="第 102 掷弹兵团",
    text="行动后，升为老兵。",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    procedures=BASE_PROCEDURES,
)

register_veteran("kards:card_102_grenadier", VETERAN)
