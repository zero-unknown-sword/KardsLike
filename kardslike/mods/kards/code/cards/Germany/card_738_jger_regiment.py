"""第 738 猎兵团"""
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
    cost=1,
    display_name="第 738 猎兵团",
    text="闪击。部署：指向 1 个单位，其被消灭时抽 1 张牌。",
    art="738_jger_regiment.png",
    rare=Rarity.LIMITED,
    at=1,
    df=1,
    operation_cost=2,
    keywords=[BLITZ],
)
