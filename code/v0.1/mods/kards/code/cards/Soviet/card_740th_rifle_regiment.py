"""步兵第 740 团"""
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
from mods.kards.code.keywords.ambush import KEYWORD as AMBUSH


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """从三张牌中开发一张"""
    player = card.controller
    candidates = [
        cards.create("kards:card_burning_sky"),
        cards.create("kards:card_the_hammer"),
        cards.create("kards:card_arctic_convoy"),
    ]
    ground.start_card_choice(
        player,
        candidates,
        card,
        destination=Zone.HAND,
        develop=True,
        title="开发一张牌",
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=5,
    display_name="步兵第 740 团",
    text="伏击。部署：从燃烧的天空、铁锤、北极护航队中开发一张。",
    art="740th_rifle_regiment.png",
    rare=Rarity.LIMITED,
    at=5,
    df=5,
    operation_cost=1,
    keywords=[AMBUSH],
    procedures=[Procedure(EventType.DEPLOY, deployed, action)],
)
