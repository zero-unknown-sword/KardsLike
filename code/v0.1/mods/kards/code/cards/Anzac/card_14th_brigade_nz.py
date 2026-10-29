"""新西兰第 14 旅"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.ANZAC,
    cost=4,
    display_name="新西兰第 14 旅",
    text="部署：若从手中最左侧部署，额外获得 1 个指挥点槽。",
    rare=Rarity.STANDARD,
    at=6,
    df=5,
    operation_cost=1,
)
