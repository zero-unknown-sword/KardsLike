"""Hs 129"""
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
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标为敌方单位。"""
    return target.is_unit and target.controller is not player


def deploy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """部署时与该敌方单位战斗。"""
    def apply(target: Card) -> None:
        ground.unit_combat(card, target)

    ground.request_target(card.controller, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=5,
    display_name="Hs 129",
    text="对抗 HQ 或陆军时具有 +2 攻击力。\n部署：与 1 个敌方单位战斗。",
    art="henschel_hs_129.png",
    rare=Rarity.SPECIAL,
    at=4,
    df=5,
    operation_cost=2,
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
