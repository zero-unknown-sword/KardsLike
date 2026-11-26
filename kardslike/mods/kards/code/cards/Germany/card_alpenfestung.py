"""阿尔卑斯要塞"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure


def action(card, event, ground):
    player = event.player
    hq = ground.hqs[player]
    hq.df = 25
    hq.max_df = 25
    hq._df.set(25)
    deck = ground.decks[player]
    for _ in range(10):
        if deck.cards:
            deck.cards.pop()


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=7,
    display_name="阿尔卑斯要塞",
    text="友方 HQ 防御力变为 25，移除友方卡组顶 10 张牌。",
    art="alpenfestung.png",
    rare=Rarity.SPECIAL,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
