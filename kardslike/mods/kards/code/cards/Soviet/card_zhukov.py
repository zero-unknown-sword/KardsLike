"""朱可夫"""
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
    Procedure,
    Rarity,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抽 1 张苏联步兵。"""
    ground.draw_filtered(
        event.player,
        lambda item: item.type is CardType.INFANTRY and item.country is Country.SOVIET,
        1,
        card,
        random_pick=False,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=1,
    display_name="朱可夫",
    text="抽 1 张苏联步兵，使其部署时获得 +1+1 和闪击。",
    art="zhukov.png",
    rare=Rarity.ELITE,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
