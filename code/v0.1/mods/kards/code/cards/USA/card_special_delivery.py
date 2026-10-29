"""特快专递"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=2,
    display_name="特快专递",
    text="弃掉手牌中所有花费不大于 2 的牌，抽 2 张牌。",
    rare=Rarity.STANDARD,
)
