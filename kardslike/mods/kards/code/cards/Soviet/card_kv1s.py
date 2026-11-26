"""KV-1S"""
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
    cost=5,
    display_name="KV-1S",
    text="守护。重甲 1。其他友方单位每有 1 个对战词条，其具有 +1 攻击力。",
    art="kv1s.png",
    rare=Rarity.LIMITED,
    at=4,
    df=5,
    operation_cost=2,
    keywords=[GUARD, ARMOR.with_val(1)],
)
