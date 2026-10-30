"""转变战法"""
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardData,
    CardTag,
    CardType,
    Country,
    Event,
    EventType,
    Procedure,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    随机将一张其他手牌洗入卡组, 然后抽 2 张牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    candidates = [item for item in ground.hands[player].cards if item is not card]
    if candidates:
        ground.put_card_into_deck(player, random.choice(candidates))

        def draw_replacement() -> None:
            for _ in range(2):
                ground.draw(player, card)

        ground.schedule_action(700, draw_replacement)
    else:
        for _ in range(2):
            ground.draw(player, card)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=1,
    display_name="转变战法",
    text="随机将 1 张手牌洗入卡组，抽 2 张牌。",
    rare=Rarity.STANDARD,
    tags=[CardTag.NOT_IN_START],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
