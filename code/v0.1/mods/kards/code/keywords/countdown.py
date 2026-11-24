"""倒计时"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, Event, EventType, KeywordData, Procedure


def turn_start(card: Card, event: Event, ground: BattleGround) -> bool:
    """在自己的回合开始时降低倒计时"""
    return (
        card.zone is not None
        and event.player is card.controller
        and card.has_keyword("countdown")
    )


def tick(card: Card, event: Event, ground: BattleGround) -> None:
    """倒计时 -1 并广播倒计时降低事件"""
    value = card.keyword_values.get("countdown")
    if not isinstance(value, int) or value <= 0:
        return
    value -= 1
    card.keyword_values["countdown"] = value
    ground.emit(
        Event(
            EventType.COUNTDOWN,
            card=card,
            player=card.controller,
            remaining=value,
        )
    )


KEYWORD = KeywordData(
    name="倒计时",
    description="此数值在控制者回合开始时 -1, 并触发倒计时降低事件",
    icon="countdown.png",
    procedures=[Procedure(EventType.TURN_START, turn_start, tick)],
)
