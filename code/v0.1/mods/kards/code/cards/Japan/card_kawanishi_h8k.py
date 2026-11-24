"""二式大艇"""
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
from mods.kards.code.weather import start_climate_choice


def friendly_forecast(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    友方预报时触发

    Args:
        card: 自身
        event: FORECAST 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return event.player is card.controller


def draw_on_forecast(card: Card, event: Event, ground: BattleGround) -> None:
    """
    友方预报时抽 1 张牌

    Args:
        card: 自身
        event: FORECAST 事件
        ground: 战斗全局参数
    """
    ground.draw(card.controller, card)


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


def deploy_forecast(card: Card, event: Event, ground: BattleGround) -> None:
    """
    部署: 预报

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数
    """
    start_climate_choice(ground, event.player, card)


CARD_DATA = CardData(
    type=CardType.BOMBER,
    country=Country.JAPAN,
    cost=6,
    display_name="二式大艇",
    text="友方预报时，抽 1 张牌。部署：预报。",
    art="kawanishi_h8k.png",
    rare=Rarity.ELITE,
    at=3,
    df=8,
    operation_cost=2,
    procedures=[
        Procedure(
            EventType.FORECAST,
            friendly_forecast,
            draw_on_forecast,
        ),
        Procedure(
            EventType.USE,
            deployed,
            deploy_forecast,
        ),
    ],
)
