"""步兵第 25 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardData,
    CardType,
    Country,
    Event,
    EventType,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=8,
    display_name="步兵第 25 团",
    text="守护。友方回合结束时，将 1 个“轻步兵”加入同一阵线。",
    art="25th_infantry_regiment.png",
    rare=Rarity.STANDARD,
    at=6,
    df=7,
    operation_cost=2,
    keywords=[GUARD],
    procedures=[
        Procedure(
            EventType.TURN_END,
            lambda card, event, ground: card.zone is Zone.BOARD and event.player is card.controller,
            lambda card, event, ground: ground.give_card(
                card.controller,
                "kards:card_light_infantry",
                Zone.BOARD,
                line=card.line,
            ),
        )
    ],
)
