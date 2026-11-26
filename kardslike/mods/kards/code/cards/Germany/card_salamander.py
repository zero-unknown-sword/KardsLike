"""He 162 蝾螈"""
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
    cost=4,
    display_name="He 162 蝾螈",
    text="闪击。本单位攻击后，移除自身，下个友方回合开始时返回战场。",
    art="salamander.png",
    rare=Rarity.LIMITED,
    at=1,
    df=2,
    operation_cost=3,
    keywords=[BLITZ],
)
