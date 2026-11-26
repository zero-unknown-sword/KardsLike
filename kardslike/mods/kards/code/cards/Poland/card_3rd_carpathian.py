"""喀尔巴阡第 3 步兵营"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=4,
    display_name="喀尔巴阡第 3 步兵营",
    text="守护。部署：将 1 个友方单位转换为钢铁师。",
    art="3rd_carpathian.png",
    rare=Rarity.STANDARD,
    at=1,
    df=2,
    operation_cost=4,
    keywords=[GUARD],
)
