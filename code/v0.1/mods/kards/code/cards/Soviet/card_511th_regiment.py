"""步兵第 511 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity
from mods.kards.code.veteran import VeteranProfile, promote, register_veteran


def damaged(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身受到伤害"""
    return event.dict.get("target") is card and not card.has_keyword("veteran")


def promote_action(card: Card, event: Event, ground: BattleGround) -> None:
    """受伤后升为老兵"""
    promote(card, ground)


BASE_PROC = Procedure(EventType.DAMAGED, damaged, promote_action)

VETERAN = VeteranProfile(
    at=3,
    df=3,
    operation_cost=1,
    art="511th_regiment_vet.png",
    text="防御力为 1 的友方步兵具有 +2 攻击力。",
    keywords=["ambush"],
    base_procedures=[BASE_PROC],
)

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="步兵第 511 团",
    text="防御力无法降为 1 以下。受到伤害后，升为老兵。",
    art="511th_regiment.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=2,
    operation_cost=1,
    procedures=[BASE_PROC],
)

register_veteran("kards:card_511th_regiment", VETERAN)
