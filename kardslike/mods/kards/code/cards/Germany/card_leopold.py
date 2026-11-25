"""利奥波德"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardTag, CardType, Country, Event, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    部署: 将所有敌方单位返回其所有者手中

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    opponent = event.player.opponent
    index = 0
    for unit in ground.units_in_effect_order(event.player):
        if unit.controller is opponent:
            ground.schedule_return(unit, card, index * 260)
            index += 1


from mods.kards.code.keywords.deployment import KEYWORD as DEPLOYMENT

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ARTILLERY,
    country=Country.GERMANY,
    cost=10,
    display_name="利奥波德",
    text="部署：将所有对方单位返回手中。",
    rare=Rarity.ELITE,
    at=6,
    df=4,
    operation_cost=3,
    keywords=[DEPLOYMENT],
    tags=[CardTag.SLAM_UP_2],
    procedures=[
        Procedure(
            DEPLOYMENT,
            lambda card, event, ground: True,
            action,
        )
    ],
)
