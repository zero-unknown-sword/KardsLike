"""KV-1 1939"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.armor import KEYWORD as ARMOR
from mods.kards.code.keywords.guard import KEYWORD as GUARD


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.SOVIET,
    cost=6,
    display_name="KV-1 1939",
    text="守护。重甲 1。",
    art="kv1_1939.png",
    rare=Rarity.SPECIAL,
    at=5,
    df=7,
    operation_cost=2,
    keywords=[GUARD, ARMOR.with_val(1)],
)
