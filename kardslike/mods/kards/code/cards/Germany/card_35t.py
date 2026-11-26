"""35T"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, EntryMethod, Event, EventType, Procedure
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.GERMANY,
    cost=2,
    display_name="35T",
    text="闪击。部署：若有友方步兵，行动花费 -1。",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=2,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: setattr(
                card, "operation_cost", max(0, card.operation_cost - 1)
            ) if any(unit.type.name == "INFANTRY" for unit in ground.support_lines[card.controller].units) else None,
        )
    ],
)
