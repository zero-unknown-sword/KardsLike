"""海军步兵第 3 旅"""
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
    cards,
)


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """召集轻步兵并将爆破加入手中"""
    player = card.controller
    token = cards.create("kards:card_light_infantry")
    ground.add_unit(player, token)
    ground.give_card(player, "kards:card_blast", Zone.HAND)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="海军步兵第 3 旅",
    text="部署：召集 1 个轻步兵，将 1 张爆破加入手中。",
    art="3rd_morskoi_pekhoty.png",
    rare=Rarity.LIMITED,
    at=1,
    df=1,
    operation_cost=1,
    procedures=[Procedure(EventType.USE, deployed, action)],
)
