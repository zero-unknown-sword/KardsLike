"""第 957 国民掷弹兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EntryMethod, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, Event, EntryMethod, EventType, Procedure, Rarity, Zone

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=2,
    display_name="第 957 国民掷弹兵团",
    text="部署：获得 1 张“生产”。",
    art="957_volksgrenadier.png",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=2,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: ground.give_card(card.controller, "kards:card_production", Zone.HAND),
        )
    ],
)
