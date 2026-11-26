"""福克 D.XXI"""
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
    EntryMethod,
    Event,
    EventType,
    Procedure,
    Rarity,
)


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抑制 1 个敌方单位。"""
    targets = [
        unit for unit in ground.all_targets()
        if unit.is_unit and unit.controller is not card.controller
    ]
    if targets:
        ground.suppress(targets[0])


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.FINLAND,
    cost=2,
    display_name="福克 D.XXI",
    text="部署：抑制 1 个敌方单位。",
    art="fokker_d_xxi.png",
    rare=Rarity.LIMITED,
    at=3,
    df=1,
    operation_cost=1,
    procedures=[Procedure(EventType.USE, deployed, action)],
)
