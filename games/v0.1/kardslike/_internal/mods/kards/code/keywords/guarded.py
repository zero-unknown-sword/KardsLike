"""被守护"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="被守护",
    description="相邻存在守护单位, 只能被轰炸机或炮兵攻击",
    icon="guarded.png",
)
