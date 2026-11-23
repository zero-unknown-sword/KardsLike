"""近卫步兵第 4 团"""
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


def enemy_drew(card: Card, event: Event, ground: BattleGround) -> bool:
    """敌方抽牌且自身在手中"""
    return (
        card.zone is Zone.HAND
        and event.player is card.controller.opponent
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """费用 -1"""
    card.apply_permanent(cost=-1)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=9,
    display_name="近卫步兵第 4 团",
    text="守护。在手中时，敌方每抽 1 张牌，费用 -1。",
    art="4th_guards_rifles.png",
    rare=Rarity.ELITE,
    at=9,
    df=9,
    operation_cost=2,
    keywords=[GUARD],
    procedures=[Procedure(EventType.DRAW, enemy_drew, action, any_zone=True)],
)
