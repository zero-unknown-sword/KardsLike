"""第 103 骑兵侦察小队"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.USA,
    cost=3,
    display_name="第 103 骑兵侦察小队",
    text="揭示：若处于隐蔽的回合数不小于 2，使所有友方单位获得 +1+1。",
    rare=Rarity.STANDARD,
    at=3,
    df=4,
    operation_cost=1,
)
