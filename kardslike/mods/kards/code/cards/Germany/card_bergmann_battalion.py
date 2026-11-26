"""山地人营"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=2,
    display_name="山地人营",
    text="山地。闪击。一回合一次，友方转换卡牌时，抽 1 张牌。",
    art="bergmann_battalion.png",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=3,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.TRANSFORM,
            lambda card, event, ground: (
                event.player is card.controller
                and card.zone is __import__("main").Zone.BOARD
                and card.last_trigger_turn != ground.turn_count
            ),
            lambda card, event, ground: (
                setattr(card, "last_trigger_turn", ground.turn_count),
                ground.draw(card.controller, card),
            ),
        )
    ],
)
