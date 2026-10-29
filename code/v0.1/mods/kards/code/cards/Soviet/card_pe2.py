"""Pe-2"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.BOMBER,
    country=Country.SOVIET,
    cost=3,
    display_name="Pe-2",
    text="轰炸机。",
    art="petlyakov_pe2.png",
    rare=Rarity.SPECIAL,
    at=4,
    df=4,
    operation_cost=3,
)
