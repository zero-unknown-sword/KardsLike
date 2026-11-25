"""标准弹药"""
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
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """使手中和卡组中的友方单位减费"""
    player = event.player
    for holder in (ground.hands[player].cards, ground.decks[player].cards):
        for unit in holder:
            if unit.is_unit and unit.controller is player:
                unit.apply_permanent(cost=-1)
                unit.operation_cost = max(0, unit.operation_cost - 1)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=0,
    display_name="标准弹药",
    text="使手中和卡组中所有友方单位获得 -1 花费和 -1 行动花费。",
    art="standard_ammo.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
