"""逼迫投降"""
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
    Player,
    Procedure,
    Rarity,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """任意单位"""
    return target.is_unit


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """压制 1 个单位, 所有被压制的敌方单位额外压制一回合"""
    player = event.player

    def apply(target: Card) -> None:
        ground.suppress(target)
        for unit in ground.units_in_effect_order(player):
            if unit.controller is not player and unit.suppressed:
                ground.extend_suppression(unit)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=1,
    display_name="逼迫投降",
    text="压制 1 个单位。所有被压制的敌方单位额外压制一回合。",
    art="forced_surrender.png",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
