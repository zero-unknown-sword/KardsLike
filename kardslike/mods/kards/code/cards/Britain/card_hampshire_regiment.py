"""汉普郡团"""
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
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """部署时触发"""
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """从三张牌中开发一张"""
    candidates = [
        cards.create("kards:card_fortification"),
        cards.create("kards:card_the_desert_rats"),
        cards.create("kards:card_convoy_hx_175"),
    ]
    ground.start_card_choice(
        card.controller,
        candidates,
        card,
        destination=Zone.HAND,
        develop=True,
        title="开发一张牌",
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=6,
    display_name="汉普郡团",
    text="守护。部署：从防御工事、沙漠之鼠、HX 175 护航队中开发一张。",
    art="hampshire_regiment.png",
    rare=Rarity.LIMITED,
    at=3,
    df=6,
    operation_cost=2,
    keywords=[GUARD],
    procedures=[Procedure(EventType.USE, deployed, action)],
)
