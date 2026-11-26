"""喀尔巴阡第 3 步兵营"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=4,
    display_name="喀尔巴阡第 3 步兵营",
    text="守护。部署：将 1 个友方单位转换为钢铁师。",
    art="3rd_carpathian.png",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=4,
    keywords=[GUARD],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: ground.request_target(
                card.controller,
                card,
                lambda target: target.is_unit and target.controller is card.controller,
                lambda target: ground.transform_unit(
                    target,
                    __import__("main").cards.create("kards:card_steel_division"),
                    source=card,
                ) if target is not None else None,
            ),
        )
    ],
)
