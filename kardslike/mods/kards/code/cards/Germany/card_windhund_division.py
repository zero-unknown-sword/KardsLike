"""灰猎犬师"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=5,
    display_name="灰猎犬师",
    text="闪击。本单位攻击并消灭单位后，可再次行动。",
    rare=Rarity.ELITE,
    at=5,
    df=8,
    operation_cost=1,
    keywords=[BLITZ],
    tags=[CardTag.REFRESH_ON_KILL],
)
