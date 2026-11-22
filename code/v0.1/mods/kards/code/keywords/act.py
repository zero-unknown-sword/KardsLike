"""行动"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="行动",
    description="撤退等行动不消耗行动次数, 也不视为移动",
    icon="",
)
