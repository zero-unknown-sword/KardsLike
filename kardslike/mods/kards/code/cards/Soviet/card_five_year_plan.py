"""五年计划"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, DamageType, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    抽 5 张牌, 然后对友方总部造成 5 点伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    for _ in range(5):
        ground.draw(player, card)
    ground.damage(ground.hqs[player], 5, card, DamageType.NONE)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=5,
    display_name="五年计划",
    text="抽 5 张牌，对友方总部造成 5 点伤害。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
