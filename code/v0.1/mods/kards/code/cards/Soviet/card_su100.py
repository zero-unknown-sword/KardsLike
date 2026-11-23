"""SU-100"""
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
)
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ


def damaged(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身受伤且尚未获得加成"""
    return (
        event.card is card
        and card.df < card.max_df
        and not card.has_tag("SU100_BONUS")
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """受伤时获得 +4 攻击力"""
    card.add_tag("SU100_BONUS")
    card.apply_permanent(at=4)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.SOVIET,
    cost=4,
    display_name="SU-100",
    text="闪击。受伤时具有 +4 攻击力。",
    art="su100.png",
    rare=Rarity.SPECIAL,
    at=4,
    df=3,
    operation_cost=1,
    keywords=[BLITZ],
    procedures=[Procedure(EventType.DAMAGED, damaged, action)],
)
