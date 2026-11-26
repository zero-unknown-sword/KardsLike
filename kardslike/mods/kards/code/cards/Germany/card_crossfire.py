"""交叉火力"""
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
    Procedure,
    Rarity,
    Zone,
)


def _crossfire(card: Card, event: Event, ground: BattleGround) -> None:
    """对所有敌方单位各造成 1 点伤害，若有单位被消灭则重复。"""
    player = event.player
    while True:
        targets = [
            unit for unit in ground.all_targets()
            if unit.is_unit and unit.controller is not player
        ]
        if not targets:
            return
        for unit in targets:
            ground.damage(unit, 1, card, DamageType.NONE)
        killed = any(unit.zone is not Zone.BOARD for unit in targets)
        if not killed:
            return


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=4,
    display_name="交叉火力",
    text="对所有敌方单位造成 1 点伤害。若有单位被消灭，重复此效果。",
    art="crossfire.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            lambda card, event, ground: _crossfire(card, event, ground),
        )
    ],
)
