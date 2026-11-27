"""第 108 装甲掷弹兵团"""
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
    Player,
    Procedure,
    Rarity,
    cards,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标为花费不大于 4 的敌方单位。"""
    return (
        target.is_unit
        and target.controller is not player
        and target.cost <= 4
    )


def _eighty_apply(card: Card, ground: BattleGround, target: Card) -> None:
    """转换目标并使其撤退。"""
    replacement = ground.transform_unit(
        target,
        cards.create("kards:card_rout_unit"),
        source=card,
    )
    if replacement is not None:
        ground.retreat_unit(replacement, card)


def deploy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """部署时转换并撤退一个敌方单位。"""
    def apply(target: Card) -> None:
        _eighty_apply(card, ground, target)

    ground.request_target(card.controller, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=7,
    display_name="第 108 装甲掷弹兵团",
    text="部署：将一个花费不大于 4 的敌方单位转换为溃军并撤退。",
    art="108_panzergrenadier.png",
    rare=Rarity.LIMITED,
    at=7,
    df=5,
    operation_cost=1,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: (
                event.card is card and event.method is EntryMethod.DEPLOY
            ),
            deploy_action,
        )
    ],
)
