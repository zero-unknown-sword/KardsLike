"""燃烧的天空"""
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
    """目标: 敌方空军"""
    return (
        target.is_unit
        and target.controller is not player
        and target.type in (CardType.FIGHTER, CardType.BOMBER)
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """对敌方空军造成 4 点伤害"""
    player = event.player

    def apply(target: Card) -> None:
        ground.damage(target, 4, card, DamageType.NONE)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=1,
    display_name="燃烧的天空",
    text="对 1 个敌方空军造成 4 点伤害。",
    art="burning_sky.png",
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
