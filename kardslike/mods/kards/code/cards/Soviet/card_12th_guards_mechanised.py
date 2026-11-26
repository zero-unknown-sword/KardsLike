"""近卫机械化第 12 旅"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.smoke import KEYWORD as SMOKE

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="近卫机械化第 12 旅",
    text="烟幕。攻击力不小于 4 的友方坦克部署时，升为老兵。",
    art="12th_guards_mechanised.png",
    rare=Rarity.STANDARD,
    at=2,
    df=1,
    operation_cost=1,
    keywords=[SMOKE],
)
