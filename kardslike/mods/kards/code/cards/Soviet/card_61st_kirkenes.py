"""希尔克内斯第 61 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="希尔克内斯第 61 团",
    text="",
    art="61st_kirkenes.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=4,
    operation_cost=1,
)
