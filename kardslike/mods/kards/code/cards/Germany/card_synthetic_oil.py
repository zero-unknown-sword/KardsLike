"""合成机油"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, Country, Event, EventType, Procedure, Rarity


def action(card, event, ground):
    player = event.player
    ground.kredits[player].credits += 10
    ground.draw(player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=0,
    display_name="合成机油",
    text="下个友方回合开始时，+10 指挥点并抽 1 张牌。",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
