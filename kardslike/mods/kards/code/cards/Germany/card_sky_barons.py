"""空中男爵"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, DamageType, Event, EventType, Procedure


def target_valid(target, player, ground):
    return target.is_unit and target.type in (CardType.FIGHTER, CardType.BOMBER)


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None:
            ground.damage(target, 99, card, DamageType.NONE)
            ground.draw(player, card)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=4,
    display_name="空中男爵",
    text="消灭 1 个空军，抽 1 张牌。",
    art="sky_barons.png",
    rare=Rarity.SPECIAL,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
