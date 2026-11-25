"""北方铁矿"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    若前线有友方单位, 获得 3 个指挥点

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    if any(unit.controller is player for unit in ground.front_line.units):
        ground.kredits[player].add_credits(3)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="北方铁矿",
    text="若前线有友方单位，获得 3 个指挥点。",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
