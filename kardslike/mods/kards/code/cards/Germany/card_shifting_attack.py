"""转变攻击"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure
from mods.kards.code.weather import add_end_cleanup


def target_valid(target, player, ground):
    return target.is_unit and target.controller is player


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None:
            old_cost = target.cost
            target.cost = 0
            add_end_cleanup(ground, player, lambda: setattr(target, "cost", old_cost))
            card.return_hand(target, ground)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=2,
    display_name="转变攻击",
    text="回手 1 个友方单位，使其花费变为 0 直到回合结束。",
    art="shifting_attack.png",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
