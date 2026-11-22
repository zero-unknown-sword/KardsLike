"""薄雾"""
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
    DamageType,
    Event,
    EventType,
    Player,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.pfwd import KEYWORD as PFWD
from mods.kards.code.keywords.climate import KEYWORD as CLIMATE
from mods.kards.code.weather import set_weather, start_forecast

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    设置天气并开始预报

    Args:
        card: 自身
        event: USE 事件
        ground: 战斗全局参数
    """
    player = event.player
    set_weather(ground, player, "rain")
    start_forecast(ground, player, card, "rain")

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=0,
    display_name="薄雾",
    text="自动使用。降雨。预报：下个友方回合获得一张降雨天气。",
    art="mist.png",
    rare=Rarity.STANDARD,
    keywords=[PFWD, CLIMATE],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
