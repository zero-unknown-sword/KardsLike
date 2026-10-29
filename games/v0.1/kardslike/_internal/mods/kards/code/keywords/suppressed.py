"""压制"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="压制",
    description="无法移动或攻击, 在所有者下个回合结束时移除",
    icon="suppressed.png",
)
