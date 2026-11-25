"""摩托化步兵第 15 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardTag, CardType, Country, Rarity
from mods.kards.code.keywords.guard import KEYWORD as GUARD

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="摩托化步兵第 15 团",
    text="守护。敌方回合中，友方总部具有免疫。",
    rare=Rarity.SPECIAL,
    at=2,
    df=5,
    operation_cost=1,
    keywords=[GUARD],
    tags=[CardTag.HQ_IMMUNE_ENEMY_TURN],
)
