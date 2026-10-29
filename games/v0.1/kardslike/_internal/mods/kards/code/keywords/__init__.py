"""KARDS 标准包关键词

每个 py 文件导出一个 KEYWORD: KeywordData
文件名即关键词 id, 图标放在 assets/keyword/{id}.png
"""

from main import KeywordData

from .ambush import KEYWORD as AMBUSH
from .armor import KEYWORD as ARMOR
from .blitz import KEYWORD as BLITZ
from .bond import KEYWORD as BOND
from .deployment import KEYWORD as DEPLOYMENT
from .destruction import KEYWORD as DESTRUCTION
from .develop import KEYWORD as DEVELOP
from .exile import KEYWORD as EXILE
from .fury import KEYWORD as FURY
from .guard import KEYWORD as GUARD
from .guarded import KEYWORD as GUARDED
from .immune import KEYWORD as IMMUNE
from .intel import KEYWORD as INTEL
from .shock import KEYWORD as SHOCK
from .smoke import KEYWORD as SMOKE
from .suppressed import KEYWORD as SUPPRESSED

KEYWORDS: dict[str, KeywordData] = {
    "ambush": AMBUSH,
    "armor": ARMOR,
    "blitz": BLITZ,
    "bond": BOND,
    "deployment": DEPLOYMENT,
    "destruction": DESTRUCTION,
    "develop": DEVELOP,
    "exile": EXILE,
    "fury": FURY,
    "guard": GUARD,
    "guarded": GUARDED,
    "immune": IMMUNE,
    "intel": INTEL,
    "shock": SHOCK,
    "smoke": SMOKE,
    "suppressed": SUPPRESSED,
}
