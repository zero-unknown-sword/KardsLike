"""Ar 196"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, EntryMethod, Event, EventType, Procedure


def deployed(card, event, ground):
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card, event, ground):
    own = len(ground.support_lines[card.controller].units)
    enemy = len(ground.support_lines[card.controller.opponent].units)
    if own <= enemy:
        ground.draw(card.controller, card)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=1,
    display_name="Ar 196",
    text="部署：若友方单位数不大于敌方，抽 1 张牌。",
    art="arado_ar_196.png",
    rare=Rarity.STANDARD,
    at=1,
    df=1,
    operation_cost=2,
    procedures=[Procedure(EventType.USE, deployed, action)],
)
