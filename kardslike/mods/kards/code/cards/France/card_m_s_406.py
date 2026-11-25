"""莫拉纳-索尼耶 M.S.406"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country

from mods.kards.code.keywords.exile import KEYWORD as EXILE

from main import Rarity

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.FRANCE,
    cost=3,
    display_name="莫拉纳-索尼耶 M.S.406",
    text="流亡：波兰。",
    art="m_s_406.png",
    rare=Rarity.STANDARD,
    at=3,
    df=3,
    operation_cost=1,
    keywords=[EXILE.with_val(Country.POLAND)],
)
