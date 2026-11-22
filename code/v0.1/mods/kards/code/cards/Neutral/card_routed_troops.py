"""溃军"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.NEUTRAL,
    cost=1,
    display_name="溃军",
    text="",
    art="routed_troops.png",
    rare=Rarity.STANDARD,
    at=1,
    df=1,
    operation_cost=1,
)
