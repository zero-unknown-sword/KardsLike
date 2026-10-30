"""租借法案"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    抽 4 张牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    for _ in range(4):
        ground.draw(event.player, card)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.BRITAIN,
    cost=7,
    display_name="租借法案",
    text="抽 4 张牌。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
