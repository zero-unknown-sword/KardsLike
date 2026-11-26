"""第 15 狼步兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, EntryMethod, Event, EventType, Procedure, Rarity, Zone

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.POLAND,
    cost=5,
    display_name="第 15 狼步兵团",
    text="部署：将 1 个单位转换为溃军；若为友方，抽 2 张牌。",
    art="15th_wolves_regiment.png",
    rare=Rarity.SPECIAL,
    at=1,
    df=4,
    operation_cost=4,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is EntryMethod.DEPLOY,
            lambda card, event, ground: ground.request_target(
                card.controller,
                card,
                lambda target: target.is_unit,
                lambda target: _wolf_apply(card, event, ground, target),
            ),
        )
    ],
)

def _wolf_apply(card, event, ground, target):
    if target is None:
        return
    friendly = target.controller is card.controller
    ground.transform_unit(target, __import__("main").cards.create("kards:card_rout_unit"), source=card)
    if friendly:
        ground.draw(card.controller, card)
        ground.draw(card.controller, card)
