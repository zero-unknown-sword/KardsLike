"""三号坦克 H 型"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.GERMANY,
    cost=4,
    display_name="三号坦克 H 型",
    text="部署：获得 1 张战利品。",
    art="panzer_iiih.png",
    rare=Rarity.LIMITED,
    at=1,
    df=2,
    operation_cost=4,
)
