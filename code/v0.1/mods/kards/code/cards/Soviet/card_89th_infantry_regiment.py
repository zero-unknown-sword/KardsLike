"""步兵第 89 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="步兵第 89 团",
    text="守护。",
    art="89th_infantry_regiment.png",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    keywords=[GUARD],
)
