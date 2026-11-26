"""霍尔姆第 99 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="霍尔姆第 99 团",
    text="闪击。部署：下个友方回合开始时，失去 1 个指挥点。",
    art="99th_kholm.png",
    rare=Rarity.STANDARD,
    at=2,
    df=2,
    operation_cost=0,
    keywords=[BLITZ],
)
