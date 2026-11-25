"""守护"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="守护",
    description="相邻的友方总部/单位获得被守护; 轰炸机与炮兵以外的单位无法攻击被守护目标",
    icon="guard.png",
)
