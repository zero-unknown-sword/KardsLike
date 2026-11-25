"""战利品"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    从卡组顶三张中选择一张, 其余置于卡组底

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.loot_from_deck(event.player, card)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=2,
    display_name="战利品",
    text="从卡组顶 3 张牌中选择 1 张并抽取，将其余 2 张置于卡组底。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
