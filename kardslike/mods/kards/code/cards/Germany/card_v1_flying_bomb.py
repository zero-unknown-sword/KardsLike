"""V-1 飞行炸弹"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, Country, DamageType, Event, EventType, Procedure, Rarity


def target_valid(target, player, ground):
    return target.is_unit and target.cost <= 3


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None:
            ground.damage(target, 99, card, DamageType.NONE)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=3,
    display_name="V-1 飞行炸弹",
    text="消灭 1 个花费不大于 3 的单位。",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
