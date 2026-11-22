"""气象"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="天气",
    description="天气效果, 每回合只能使用一次",
    icon="",
)
