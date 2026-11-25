"""四号坦克 G 型"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.GERMANY,
    cost=5,
    display_name="四号坦克 G 型",
    text="",
    rare=Rarity.STANDARD,
    at=5,
    df=6,
    operation_cost=2,
)
