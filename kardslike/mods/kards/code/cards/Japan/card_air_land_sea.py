"""海陆空"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity
from mods.kards.code.keywords.develop import KEYWORD as DEVELOP, execute as develop


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    失去 1 个指挥点槽, 开发 1 张构筑外的牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.kredits[event.player].remove_slots(1)
    develop(ground, event.player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=1,
    display_name="海陆空",
    text="开发 1 张构筑外的牌。失去 1 个指挥点槽。",
    rare=Rarity.LIMITED,
    keywords=[DEVELOP],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
