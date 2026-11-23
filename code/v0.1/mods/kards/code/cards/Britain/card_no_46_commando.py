"""第 46 突击队"""
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
    Zone,
)


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """将爆破和计划加入手中"""
    player = card.controller
    ground.give_card(player, "kards:card_blast", Zone.HAND)
    ground.give_card(player, "kards:card_plan", Zone.HAND)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=1,
    display_name="第 46 突击队",
    text="突击队。部署：将 1 张爆破和 1 张计划加入手中。",
    art="no_46_commando.png",
    rare=Rarity.STANDARD,
    at=1,
    df=1,
    operation_cost=1,
    sub_type="commando",
    procedures=[Procedure(EventType.DEPLOY, deployed, action)],
)
