"""三号坦克 H 型"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity, Zone

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.GERMANY,
    cost=4,
    display_name="三号坦克 H 型",
    text="部署：获得 1 张战利品。",
    art="panzer_iiih.png",
    rare=Rarity.LIMITED,
    at=1,
    df=2,
    operation_cost=4,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: ground.give_card(card.controller, "kards:card_spoils_of_war", Zone.HAND),
        )
    ],
)
