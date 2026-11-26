"""溃敌"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure


def target_valid(target, player, ground):
    return target.is_unit


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None and target.cost <= 2:
            template = __import__("main").cards.create("kards:card_rout_unit")
            ground.transform_unit(target, template, source=card)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="溃敌",
    text="将 1 个花费不大于 2 的单位转换为溃军。",
    art="rout.png",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
