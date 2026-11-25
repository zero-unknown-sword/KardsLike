"""鄂木斯克第 132 团"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="鄂木斯克第 132 团",
    text="部署：每有 1 个对战词条数不小于 2 的友方单位，获得一次 +1+1。",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=1,
)
