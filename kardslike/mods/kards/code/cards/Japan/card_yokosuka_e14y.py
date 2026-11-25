"""零式小型水侦"""
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
    EntryMethod,
    Event,
    EventType,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.weather import start_climate_choice


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    部署时触发

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    部署: 预报

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数
    """
    start_climate_choice(ground, event.player, card)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.JAPAN,
    cost=3,
    display_name="零式小型水侦",
    text="闪击。部署：预报。",
    art="yokosuka_e14y.png",
    rare=Rarity.LIMITED,
    at=2,
    df=2,
    operation_cost=1,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.USE,
            deployed,
            action,
        )
    ],
)
