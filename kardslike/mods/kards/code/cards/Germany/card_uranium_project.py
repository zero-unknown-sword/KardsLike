"""铀工程"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardType, Country, DamageType, Event, EventType, Procedure, Rarity


def action(card, event, ground):
    player = event.player
    enemies = [unit for unit in list(ground.all_targets()) if unit.is_unit and unit.controller is not player]
    for unit in enemies:
        ground.damage(unit, 99, card, DamageType.NONE)
        ground.kredits[player].credits += 1


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=12,
    display_name="铀工程",
    text="消灭所有敌方单位；每消灭 1 个，获得 1 个指挥点。",
    rare=Rarity.ELITE,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
