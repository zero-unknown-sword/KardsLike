"""持续弹幕"""
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
    Player,
    Procedure,
    Rarity,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    return target.is_unit


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对一个单位造成 6 点伤害。"""
    player = event.player

    def apply(target: Card | None) -> None:
        if target is not None:
            ground.damage(target, 6, card, DamageType.NONE)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=2,
    display_name="持续弹幕",
    text="对 1 个单位造成 6 点伤害。下个友方回合开始时，失去 2 个指挥点。",
    art="extended_barrage.png",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
