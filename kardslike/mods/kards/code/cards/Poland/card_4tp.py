"""4TP"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.POLAND,
    cost=1,
    display_name="4TP",
    text="闪击。攻击敌方 HQ 后消灭自身。",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=3,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.ATTACK,
            lambda card, event, ground: event.card is card and event.target.is_hq,
            lambda card, event, ground: card.destroy(card, ground),
        )
    ],
)
