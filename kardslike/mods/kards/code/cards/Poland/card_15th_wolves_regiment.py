"""第 15 狼步兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=5,
    display_name="第 15 狼步兵团",
    text="部署：将 1 个单位转换为溃军；若为友方，抽 2 张牌。",
    art="15th_wolves_regiment.png",
    rare=Rarity.SPECIAL,
    at=1,
    df=4,
    operation_cost=4,
)
