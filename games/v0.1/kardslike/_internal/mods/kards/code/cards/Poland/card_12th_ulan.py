"""第 12 乌兰骑兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.fury import KEYWORD as FURY

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=1,
    display_name="第 12 乌兰骑兵团",
    text="闪击, 奋战。",
    rare=Rarity.LIMITED,
    at=3,
    df=1,
    operation_cost=1,
    keywords=[BLITZ, FURY],
)
