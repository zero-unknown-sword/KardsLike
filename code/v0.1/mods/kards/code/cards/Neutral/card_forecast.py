"""预报"""
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
    Player,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.forecast import KEYWORD as FORECAST
from mods.kards.code.weather import start_climate_choice


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    从蓝天、薄雾、狂风中选择一种气象

    Args:
        card: 自身
        event: USE 事件
        ground: 战斗全局参数
    """
    start_climate_choice(ground, event.player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=0,
    display_name="预报",
    text="选择一种气象。气象进入手牌时自动使用。",
    art="",
    rare=Rarity.STANDARD,
    keywords=[FORECAST],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
