"""第 738 猎兵团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=1,
    display_name="第 738 猎兵团",
    text="闪击。部署：指向 1 个单位，其被消灭时抽 1 张牌。",
    art="738_jger_regiment.png",
    rare=Rarity.LIMITED,
    at=1,
    df=2,
    operation_cost=1,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.card is card and event.method is __import__("main").EntryMethod.DEPLOY,
            lambda card, event, ground: ground.request_target(
                card.controller,
                card,
                lambda target: target.is_unit,
                lambda target: setattr(card, "listen_target", target) if target is not None else None,
            ),
        ),
        Procedure(
            EventType.LEAVE,
            lambda card, event, ground: (
                card.zone is Zone.BOARD
                and not card.suppressed
                and getattr(card, "listen_target", None) is event.card
            ),
            lambda card, event, ground: ground.draw(card.controller, card),
        ),
    ],
)
