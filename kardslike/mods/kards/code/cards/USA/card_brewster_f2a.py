"""F2A 水牛"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country, Event, EventType, Procedure, BattleGround, Card

from main import Rarity


def front_line_aura(card: Card, event: Event, ground: BattleGround) -> None:
    """
    位于前线时获得 +1 攻击力

    光环每个 LOOP 先被清除, 再由本流程重新应用

    Args:
        card: 水牛
        event: LOOP 事件
        ground: 战斗全局参数
    """
    if card.line is ground.front_line:
        card.add_aura(at=1)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.USA,
    cost=1,
    display_name="F2A 水牛",
    text="位于前线时具有 +2 攻击力。",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=1,
    tags=[CardTag.NOT_IN_START],
    procedures=[Procedure(EventType.LOOP, lambda card, event, ground: True, front_line_aura)],
)
