"""总参二局"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    抽 1 张牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.draw(event.player)


from mods.kards.code.keywords.intel import KEYWORD as INTEL

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.POLAND,
    cost=2,
    display_name="总参二局",
    text="情报 2。抽 1 张牌。",
    rare=Rarity.SPECIAL,
    keywords=[INTEL.with_val(2)],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
