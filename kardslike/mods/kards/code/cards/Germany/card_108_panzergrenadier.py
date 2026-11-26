"""第 108 装甲掷弹兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=7,
    display_name="第 108 装甲掷弹兵团",
    text="部署：将一个花费不大于 4 的敌方单位转换为溃军并撤退。",
    art="108_panzergrenadier.png",
    rare=Rarity.LIMITED,
    at=1,
    df=5,
    operation_cost=6,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: ground.request_target(
                card.controller,
                card,
                lambda target: target.is_unit and target.controller is not card.controller and target.cost <= 4,
                lambda target: _eighty_apply(card, ground, target),
            ),
        )
    ],
)

def _eighty_apply(card, ground, target):
    if target is None:
        return
    replacement = ground.transform_unit(
        target, __import__("main").cards.create("kards:card_rout_unit"), source=card
    )
    if replacement is not None:
        ground.retreat_unit(replacement, card)
