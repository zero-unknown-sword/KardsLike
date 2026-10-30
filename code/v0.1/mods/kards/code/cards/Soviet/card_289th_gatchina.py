"""加特契纳第 289 团"""
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
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.bond import KEYWORD as BOND
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION


def last_rites(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 抽 1 张牌, 友方总部获得等同于其花费的防御力

    Args:
        card: 自身
        event: LEAVE 事件
        ground: 战斗全局参数
    """
    player = card.controller
    # 获取抽到的卡牌
    drawn = ground.draw(player, card)
    if drawn:
        ground.hqs[player].buff(df=drawn.cost)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="加特契纳第 289 团",
    text="闪击, 协力。亡计：抽 1 张牌。使友方总部获得等同于其花费的防御力。",
    art="289th_gatchina.png",
    rare=Rarity.ELITE,
    at=5,
    df=2,
    operation_cost=2,
    keywords=[BLITZ, BOND, DESTRUCTION],
    procedures=[
        Procedure(
            DESTRUCTION,
            lambda card, event, ground: event.card is card,
            last_rites,
        )
    ],
)
