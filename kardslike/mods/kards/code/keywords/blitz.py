"""闪击"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardTag, EventType, KeywordData, Procedure

KEYWORD = KeywordData(
    name="闪击",
    description="拥有此关键词的单位可在部署或加入的同一回合内行动",
    icon="",
    procedures=[
        Procedure(
            EventType.ENTER,
            lambda card, event, ground: event.card is card,
            lambda card, event, ground: card.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER),
        )
    ],
)
