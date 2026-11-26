"""以剑之名"""
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
    """抽取等同于敌方单位数量的卡牌。"""
    player = event.player
    enemy_units = [
        unit
        for unit in ground.all_targets()
        if unit.is_unit and unit.controller is not player
    ]
    for _ in enemy_units:
        ground.draw(player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=4,
    display_name="以剑之名",
    text="抽取等同于敌方单位数量的卡牌。",
    art="by_the_sword.png",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
