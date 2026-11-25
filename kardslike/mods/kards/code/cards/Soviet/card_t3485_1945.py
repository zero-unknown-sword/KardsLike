"""T-34-85 1945"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country, Rarity
from mods.kards.code.keywords.armor import KEYWORD as ARMOR
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.shock import KEYWORD as SHOCK

CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.SOVIET,
    cost=6,
    display_name="T-34-85 1945",
    text="闪击。冲击。重甲 1。无法失去冲击或被抑制。",
    art="t3485_1945.png",
    rare=Rarity.ELITE,
    at=6,
    df=6,
    operation_cost=2,
    keywords=[BLITZ, SHOCK, ARMOR.with_val(1)],
    tags=[CardTag.KEEP_SHOCK, CardTag.UNINHIBITABLE],
)
