"""BM-13N US6"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.ARTILLERY,
    country=Country.SOVIET,
    cost=3,
    display_name="BM-13N US6",
    text="闪击。本单位被攻击时，在伤害造成前撤退。",
    art="bm13n_us6.png",
    rare=Rarity.ELITE,
    at=2,
    df=2,
    operation_cost=1,
    keywords=[BLITZ],
)
