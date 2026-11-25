"""亡计"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import EventType, KeywordData, LeaveMethod

KEYWORD = KeywordData(
    name="亡计",
    description="被消灭时触发的效果",
    icon="destruction.png",
    trigger=EventType.LEAVE,
    trigger_condition=lambda card, event, ground: event.card is card
    and event.dict.get("way") == LeaveMethod.DESTROYED,
)
