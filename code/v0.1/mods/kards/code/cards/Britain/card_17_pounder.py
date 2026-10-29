"""17 磅炮"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ARTILLERY,
    country=Country.BRITAIN,
    cost=4,
    display_name="17 磅炮",
    text="部署：压制 1 个敌方单位。若是坦克，抽 1 张牌。",
    rare=Rarity.LIMITED,
    at=2,
    df=3,
    operation_cost=1,
)
