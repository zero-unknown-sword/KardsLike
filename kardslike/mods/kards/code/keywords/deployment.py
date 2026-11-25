"""部署"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import EntryMethod, EventType, KeywordData

KEYWORD = KeywordData(
    name="部署",
    description="部署时触发的效果",
    icon="",
    trigger=EventType.ENTER,
    trigger_condition=lambda card, event, ground: event.card is card
    and event.method == EntryMethod.DEPLOY,
)
