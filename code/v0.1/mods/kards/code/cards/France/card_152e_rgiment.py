"""第 152 团"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.FRANCE,
    cost=1,
    display_name="第 152 团",
    text="若友方指挥点槽数小于 6，无法部署。",
    rare=Rarity.STANDARD,
    at=3,
    df=3,
    operation_cost=3,
)
