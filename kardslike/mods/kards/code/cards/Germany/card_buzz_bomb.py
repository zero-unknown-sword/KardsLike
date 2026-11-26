"""嗡嗡炸弹"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, DamageType, Event, EventType, Procedure


def target_valid(target, player, ground):
    return target.is_unit or target.is_hq


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is None:
            return
        ground.damage(target, 1, card, DamageType.NONE)
        if target.is_hq:
            ground.draw(player, card)

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="嗡嗡炸弹",
    text="对 1 个敌方目标造成 1 点伤害，若为 HQ，抽 1 张牌。",
    art="buzz_bomb.png",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
