"""预报"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="预报",
    description="选择一种气象, 并在下个友方回合获得对应的天气",
    icon="",
)
