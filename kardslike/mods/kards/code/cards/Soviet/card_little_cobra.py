"""P-39 小蛇"""
import random
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
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """随机消灭另一个友方单位"""
    player = card.controller
    targets = [
        unit
        for unit in ground.units_in_effect_order(player)
        if unit.controller is player and unit is not card
    ]
    if targets:
        ground.kill(random.choice(targets), card)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.SOVIET,
    cost=3,
    display_name="P-39 小蛇",
    text="闪击。部署：随机消灭 1 个其他友方单位。",
    art="little_cobra.png",
    rare=Rarity.SPECIAL,
    at=4,
    df=5,
    operation_cost=2,
    keywords=[BLITZ],
    procedures=[Procedure(EventType.USE, deployed, action)],
)
