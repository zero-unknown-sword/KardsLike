"""自动使用"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="自动使用",
    description="进入手牌时自动使用, 花费视为 0",
    icon="",
)
