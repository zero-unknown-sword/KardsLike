"""第 102 掷弹兵团"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=1,
    display_name="第 102 掷弹兵团",
    text="行动后，升为老兵。",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
)
