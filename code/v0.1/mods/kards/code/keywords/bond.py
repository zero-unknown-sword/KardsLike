"""协力"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import KeywordData

KEYWORD = KeywordData(
    name="协力",
    description="使用本卡时, 若本回合开始时场上没有同国家友方单位, 总部受到士气伤害",
    icon="",
)
