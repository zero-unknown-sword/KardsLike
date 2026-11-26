"""血红镰刀"""
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
    """对目标与友方总部各造成 1 点伤害，然后抽 1 张牌。"""
    player = event.player

    def apply(target: Card | None) -> None:
        if target is not None:
            ground.damage(target, 1, card, DamageType.NONE)
        ground.damage(ground.hqs[player], 1, card, DamageType.NONE)
        ground.draw(player, card)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=1,
    display_name="血红镰刀",
    text="对 1 个单位和友方总部造成 1 点伤害，抽 1 张牌。",
    art="bloody_sickle.png",
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
