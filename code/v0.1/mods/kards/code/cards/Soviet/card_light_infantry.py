"""轻步兵"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="轻步兵",
    text="",
    rare=Rarity.STANDARD,
    at=1,
    df=1,
    operation_cost=0,
    tags=[CardTag.NOT_IN_START],
)
