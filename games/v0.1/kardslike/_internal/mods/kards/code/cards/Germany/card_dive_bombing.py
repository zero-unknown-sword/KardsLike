"""俯冲轰炸"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="俯冲轰炸",
    text="对 1 个敌方单位造成 1 点伤害。使其攻击力为 0，直到下个友方回合开始。",
    rare=Rarity.STANDARD,
)
