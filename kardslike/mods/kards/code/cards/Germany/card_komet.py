"""Me 163 彗星"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=6,
    display_name="Me 163 彗星",
    text="闪击。友方回合结束时，若在场上，回手。",
    art="komet.png",
    rare=Rarity.ELITE,
    at=0,
    df=4,
    operation_cost=2,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.TURN_END,
            lambda card, event, ground: card.zone is Zone.BOARD and event.player is card.controller,
            lambda card, event, ground: card.return_hand(card, ground),
        )
    ],
)
