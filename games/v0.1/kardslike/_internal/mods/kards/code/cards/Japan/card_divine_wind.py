"""神风行动"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=3,
    display_name="神风行动",
    text="消灭 1 个单位，随机弃 1 张牌。",
    rare=Rarity.SPECIAL,
)
