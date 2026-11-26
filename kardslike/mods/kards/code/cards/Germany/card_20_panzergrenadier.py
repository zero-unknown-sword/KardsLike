"""第 20 装甲掷弹兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=5,
    display_name="第 20 装甲掷弹兵团",
    text="闪击。部署：获得 1 张 35T 和 1 张协同作战。",
    art="20_panzergrenadier.png",
    rare=Rarity.SPECIAL,
    at=1,
    df=3,
    operation_cost=4,
    keywords=[BLITZ],
)
