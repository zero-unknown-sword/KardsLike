"""交叉火力"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, DamageType, Event, EventType, Procedure

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=4,
    display_name="交叉火力",
    text="对两个敌方单位各造成 2 点伤害。",
    art="crossfire.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            lambda card, event, ground: [
                ground.damage(unit, 2, card, DamageType.NONE)
                for unit in list(ground.all_targets())
                if unit.is_unit and unit.controller is not event.player
            ][:2],
        )
    ],
)
