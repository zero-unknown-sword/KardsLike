"""UUIX 级潜艇"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, Country, DamageType, Event, EventType, Procedure, Rarity


def target_valid(target, player, ground):
    return target.is_unit and target.controller is not player


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None:
            ground.damage(target, 99, card, DamageType.NONE)
            for _ in range(2):
                if ground.hands[player.opponent].cards:
                    discarded = ground.hands[player.opponent].cards.pop()
                    ground.discards[player.opponent].add(discarded)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=4,
    display_name="UUIX 级潜艇",
    text="消灭 1 个敌方单位；对手随机弃 2 张牌。",
    rare=Rarity.SPECIAL,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
