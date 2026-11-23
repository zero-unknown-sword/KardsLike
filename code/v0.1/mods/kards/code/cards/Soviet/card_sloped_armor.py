"""倾斜装甲"""
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
    Zone,
    cards,
)
from mods.kards.code.weather import add_end_cleanup


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 敌方单位"""
    return target.is_unit and target.controller is not player


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """召集 IS-2 与目标战斗，结束回合时回手"""
    player = event.player

    def apply(target: Card) -> None:
        is2 = cards.create("kards:card_iosef_stalin_ii")
        if not ground.add_unit(player, is2):
            return
        ground.unit_combat(is2, target)

        def return_is2() -> None:
            if is2.zone is Zone.BOARD:
                ground.return_unit(is2, card)

        add_end_cleanup(ground, player, return_is2)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=0,
    display_name="倾斜装甲",
    text="指向 1 个敌方单位，召集 1 个 IS-2，使两者战斗。回合结束时，将 IS-2 回手。",
    art="sloped_armor.png",
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
