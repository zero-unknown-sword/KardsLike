"""Me 163 彗星"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=6,
    display_name="Me 163 彗星",
    text="闪击。友方回合结束时，若在场上，回手。",
    art="komet.png",
    rare=Rarity.ELITE,
    at=0,
    df=4,
    operation_cost=2,
    keywords=[BLITZ],
)
