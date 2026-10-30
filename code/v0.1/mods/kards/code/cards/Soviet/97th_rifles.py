"""步兵第 97 团"""
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
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.guard import KEYWORD as GUARD
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION


def last_rites(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 抽 1 张牌, 将 1 张步兵第 414 团洗入卡组

    Args:
        card: 自身
        event: LEAVE 事件
        ground: 战斗全局参数
    """
    player = card.controller
    ground.give_card(player, "kards:card_414th_rifles", Zone.DECK)
    ground.schedule_action(
        ground.add_deck_delay + 610,
        lambda: ground.shuffle_deck(player),
    )
    ground.draw(player, card)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=1,
    display_name="步兵第 97 团",
    text="守护。亡计：将 1 张“步兵第 414 团”洗入卡组，抽 1 张牌。",
    art="97th_rifles.png",
    rare=Rarity.ELITE,
    at=1,
    df=2,
    operation_cost=1,
    keywords=[GUARD, DESTRUCTION],
    procedures=[
        Procedure(
            DESTRUCTION,
            lambda card, event, ground: event.card is card,
            last_rites,
        )
    ],
)
