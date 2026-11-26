"""钢铁师"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure, Zone
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=5,
    display_name="钢铁师",
    text="守护。友方回合开始时抽 1 张牌，第三次后消灭自身。",
    rare=Rarity.SPECIAL,
    at=6,
    df=6,
    operation_cost=1,
    keywords=[GUARD],
    procedures=[
        Procedure(
            EventType.TURN_START,
            lambda card, event, ground: card.zone is Zone.BOARD and event.player is card.controller,
            lambda card, event, ground: _steel_start(card, ground),
        )
    ],
)

def _steel_start(card, ground):
    ground.draw(card.controller, card)
    card.steel_count = getattr(card, "steel_count", 0) + 1
    if card.steel_count >= 3:
        card.destroy(card, ground)
