"""战争债券"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    获得 2 个指挥点槽, 下个友方回合开始时抽 1 张牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.kredits[event.player].add_slots(2)
    ground.pending_turn_draws[event.player] += 1


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=5,
    display_name="战争债券",
    text="额外获得 2 个指挥点槽。下个友方回合开始时，抽 1 张牌。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
