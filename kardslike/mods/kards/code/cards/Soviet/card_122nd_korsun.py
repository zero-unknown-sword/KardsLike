"""科尔孙第 122 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=6,
    display_name="科尔孙第 122 团",
    text="守护。每有 1 个友方单位，具有 -1 花费。",
    art="122nd_korsun.png",
    rare=Rarity.ELITE,
    at=5,
    df=7,
    operation_cost=1,
    keywords=[GUARD],
)
