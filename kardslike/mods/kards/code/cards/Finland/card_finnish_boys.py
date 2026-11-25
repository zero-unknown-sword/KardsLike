"""芬兰男孩步兵团"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.FINLAND,
    cost=3,
    display_name="芬兰男孩步兵团",
    text="友方手牌无法被弃掉。",
    rare=Rarity.SPECIAL,
    at=2,
    df=7,
    operation_cost=1,
)
