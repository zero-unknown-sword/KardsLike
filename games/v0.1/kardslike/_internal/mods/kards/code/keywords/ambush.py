"""伏击"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="伏击",
    description="每回合首次被攻击时, 若反击伤害足以消灭攻击者, 免疫本次伤害",
    icon="ambush.png",
)
