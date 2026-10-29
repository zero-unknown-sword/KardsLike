"""加州第 2 步兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country

from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.USA,
    cost=5,
    display_name="加州第 2 步兵团",
    text="闪击。本单位受到的对战伤害至多为 1。",
    rare=Rarity.SPECIAL,
    at=5,
    df=3,
    operation_cost=1,
    keywords=[BLITZ],
    tags=[CardTag.DAMAGE_CAP_ONE, CardTag.SLAM_UP_1],
)
