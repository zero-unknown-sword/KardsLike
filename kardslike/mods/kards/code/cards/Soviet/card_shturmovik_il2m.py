"""伊尔-2M"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country
from mods.kards.code.keywords.armor import KEYWORD as ARMOR

from main import Rarity

CARD_DATA = CardData(
    type=CardType.BOMBER,
    country=Country.SOVIET,
    cost=4,
    display_name="伊尔-2M",
    text="重甲 1。本单位攻击并消灭 1 个单位后，溢出的伤害会转移到敌方总部。",
    rare=Rarity.SPECIAL,
    at=4,
    df=3,
    operation_cost=2,
    keywords=[ARMOR.with_val(1)],
    tags=[CardTag.OVERFLOW_DAMAGE],
)
