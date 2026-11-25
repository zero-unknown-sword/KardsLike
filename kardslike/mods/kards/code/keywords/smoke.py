"""烟幕"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import EventType, KeywordData, LineKind, Procedure


def lose_smoke(card, event, ground) -> None:
    """
    失去烟幕

    Args:
        card: 卡牌
        event: 事件
        ground: 战斗全局参数
    """
    if "smoke" in card.keywords:
        card.keywords.remove("smoke")


KEYWORD = KeywordData(
    name="烟幕",
    description="无法被单位攻击; 位于前线或移动/攻击后失去",
    icon="smoke.png",
    procedures=[
        Procedure(
            EventType.MOVE,
            lambda card, event, ground: event.dict.get("card") is card,
            lose_smoke,
        ),
        Procedure(
            EventType.ATTACK,
            lambda card, event, ground: event.dict.get("card") is card,
            lose_smoke,
        ),
        Procedure(
            EventType.ENTER,
            lambda card, event, ground: card.line is not None
            and card.line.kind is LineKind.FRONT,
            lose_smoke,
        ),
    ],
)
