"""Hs 129"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import CardData, CardType, Country, Rarity

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=5,
    display_name="Hs 129",
    text="对抗 HQ 或陆军时具有 +2 攻击力。部署：与 1 个敌方单位战斗。",
    art="henschel_hs_129.png",
    rare=Rarity.SPECIAL,
    at=2,
    df=4,
    operation_cost=5,
)
