"""抑制"""
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
        if target is None:
            return
        ground.suppress(target)
        if any(unit.type.name in {"FIGHTER", "BOMBER"} and unit.controller is player for unit in ground.all_targets()):
            ground.draw(player, card)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="抑制",
    text="抑制 1 个单位。若有友方空军，抽 1 张牌。",
    art="suppression.png",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
