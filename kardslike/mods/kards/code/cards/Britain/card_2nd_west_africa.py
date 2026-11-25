"""第 2 西非旅"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardData,
    CardType,
    Country,
    EntryMethod,
    Event,
    EventType,
    Procedure,
    Rarity,
)


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抽取卡组中花费最低的指令"""
    ground.draw_filtered(
        card.controller,
        lambda item: item.type is CardType.ORDER,
        1,
        card,
        random_pick=False,
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=2,
    display_name="第 2 西非旅",
    text="部署：抽取卡组中花费最低的指令。",
    art="2nd_west_africa.png",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    procedures=[Procedure(EventType.USE, deployed, action)],
)
