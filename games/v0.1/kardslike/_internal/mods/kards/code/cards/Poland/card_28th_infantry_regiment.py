"""第 28 步兵团"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=2,
    display_name="第 28 步兵团",
    text="本单位对战并存活后，获得 +1+1。",
    rare=Rarity.LIMITED,
    at=2,
    df=3,
    operation_cost=0,
    keywords=[BLITZ],
)
