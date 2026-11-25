"""免疫"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="免疫",
    description="不会受到伤害, 士气伤害除外",
    icon="immune.png",
)
