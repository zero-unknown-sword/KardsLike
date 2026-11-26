"""生产"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=0,
    display_name="生产",
    text="",
    rare=Rarity.STANDARD,
)
