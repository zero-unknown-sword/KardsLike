"""KM 提尔皮茨号"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, DamageType, Event, EventType, Procedure


def action(card, event, ground):
    enemy = event.player.opponent
    ground.damage(ground.hqs[enemy], 4, card, DamageType.NONE)
    locks = getattr(ground, "deploy_lock", {})
    locks[enemy] = ground.turn_count + 1
    ground.deploy_lock = locks


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=5,
    display_name="KM 提尔皮茨号",
    text="对敌方 HQ 造成 4 点伤害；下个敌方回合无法部署单位。",
    art="km_tirpitz.png",
    rare=Rarity.SPECIAL,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
