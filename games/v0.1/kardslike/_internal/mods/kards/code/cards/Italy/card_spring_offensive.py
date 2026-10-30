"""春季攻势

KL:
<|使用|>: <源 == 自身> -> /全局. 抽牌(2)\\
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    抽 2 张牌, 每抽到 1 张攻击力不小于 4 的单位获得 2 个指挥点

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    for _ in range(2):
        drawn = ground.draw(player, card)
        if drawn is not None and drawn.is_unit and drawn.at >= 4:
            ground.kredits[player].add_credits(2)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.ITALY,
    cost=4,
    display_name="春季攻势",
    text="抽 2 张牌。每抽到 1 张攻击力不小于 4 的单位，获得 2 个指挥点。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
