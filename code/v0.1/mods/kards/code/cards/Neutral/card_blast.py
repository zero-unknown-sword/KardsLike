"""爆破"""
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
    """目标: 任意单位"""
    return target.is_unit


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对目标造成 1 点伤害"""
    player = event.player

    def apply(target: Card) -> None:
        ground.damage(target, 1, card, DamageType.NONE)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=0,
    display_name="爆破",
    text="对 1 个单位造成 1 点伤害。",
    art="blast.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
