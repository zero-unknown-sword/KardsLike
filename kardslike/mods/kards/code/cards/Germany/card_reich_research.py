"""德意志帝国研发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=3,
    display_name="德意志帝国研发",
    text="研发：选择一项德国研发产物。",
    art="reich_research.png",
    rare=Rarity.STANDARD,
)
