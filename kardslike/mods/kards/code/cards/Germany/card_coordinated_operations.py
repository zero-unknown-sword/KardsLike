"""协同作战"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, Event, EventType, Procedure


def target_valid(target, player, ground):
    return target.is_unit and target.type.name == "TANK" and target.controller is player


def action(card, event, ground):
    player = event.player

    def apply(target):
        if target is not None:
            kinds = {unit.type for unit in ground.all_targets() if unit.is_unit and unit.controller is player}
            target.apply_permanent(at=len(kinds), df=len(kinds))
            ground.buff(target, at=len(kinds), df=len(kinds))

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="协同作战",
    text="使 1 个友方坦克获得等同于友方单位类型数的攻击力和防御力。",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
