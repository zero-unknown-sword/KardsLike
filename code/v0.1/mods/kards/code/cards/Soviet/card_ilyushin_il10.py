"""伊尔-10"""
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
    Event,
    EventType,
    LeaveMethod,
    Procedure,
    Rarity,
    cards,
)


def destroyed(card: Card, event: Event, ground: BattleGround) -> bool:
    """自身被消灭时触发"""
    return (
        event.dict.get("card") is card
        and event.dict.get("way") == LeaveMethod.DESTROYED
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """召集最后被消灭的友方陆军"""
    player = card.controller
    last = ground.last_destroyed_ground[player]
    if last is None:
        return
    token = cards.create(last.card_id)
    ground.add_unit(player, token)


CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.SOVIET,
    cost=3,
    display_name="伊尔-10",
    text="亡计：召集上个被消灭的友方陆军。",
    art="ilyushin_il10.png",
    rare=Rarity.ELITE,
    at=4,
    df=3,
    operation_cost=1,
    procedures=[Procedure(EventType.LEAVE, destroyed, action)],
)
