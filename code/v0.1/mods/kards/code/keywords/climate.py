"""气象"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="气象",
    description="蓝天、薄雾或狂风, 进入手牌时自动使用",
    icon="",
)
