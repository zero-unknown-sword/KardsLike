"""第 108 装甲掷弹兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=7,
    display_name="第 108 装甲掷弹兵团",
    text="部署：将一个花费不大于 4 的敌方单位转换为溃军并撤退。",
    art="108_panzergrenadier.png",
    rare=Rarity.LIMITED,
    at=1,
    df=5,
    operation_cost=6,
)
