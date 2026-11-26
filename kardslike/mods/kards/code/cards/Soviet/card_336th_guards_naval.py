"""近卫海军步兵第 336 旅"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=4,
    display_name="近卫海军步兵第 336 旅",
    text="部署：选择手中的 1 张花费不大于 3 的单位。将 1 个复制加入支援阵线。",
    art="336th_guards_naval.png",
    rare=Rarity.ELITE,
    at=3,
    df=4,
    operation_cost=1,
)
