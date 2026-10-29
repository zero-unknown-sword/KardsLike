"""La-5"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.SOVIET,
    cost=4,
    display_name="La-5",
    text="战斗机。",
    rare=Rarity.LIMITED,
    at=4,
    df=5,
    operation_cost=2,
)
