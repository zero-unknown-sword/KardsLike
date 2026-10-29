"""冲击"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import EventType, KeywordData, Procedure


def lose_shock(card, event, ground) -> None:
    """
    攻击后失去冲击

    Args:
        card: 卡牌
        event: 事件
        ground: 战斗全局参数
    """
    if "shock" in card.keywords:
        card.keywords.remove("shock")


KEYWORD = KeywordData(
    name="冲击",
    description="攻击时不会被反击; 攻击后失去冲击",
    icon="shock.png",
    procedures=[
        Procedure(
            EventType.ATTACK,
            lambda card, event, ground: event.dict.get("card") is card,
            lose_shock,
        )
    ],
)
