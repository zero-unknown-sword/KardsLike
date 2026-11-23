"""KV-1 1941"""
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
)
from mods.kards.code.keywords.armor import KEYWORD as ARMOR


def enemy_drew(card: Card, event: Event, ground: BattleGround) -> bool:
    """敌方抽牌"""
    return event.player is card.controller.opponent


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对敌方总部造成 2 点伤害"""
    enemy = card.controller.opponent
    ground.damage(ground.hqs[enemy], 2, card, DamageType.NONE)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.SOVIET,
    cost=6,
    display_name="KV-1 1941",
    text="重甲 1。敌方每抽 1 张牌，对其总部造成 2 点伤害。",
    art="kv1_1941.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=6,
    operation_cost=2,
    keywords=[ARMOR.with_val(1)],
    procedures=[Procedure(EventType.DRAW, enemy_drew, action)],
)
