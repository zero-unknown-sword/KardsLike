"""步兵第 414 团"""
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
    DamageType,
    Event,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION


def last_rites(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 抽 3 张牌, 友方 HQ 受 3 点伤害, 洗 1 张步兵第 97 团进卡组

    Args:
        card: 自身
        event: LEAVE 事件
        ground: 战斗全局参数
    """
    player = card.controller
    for _ in range(3):
        ground.draw(player, card)
    ground.damage(ground.hqs[player], 3, card, DamageType.NONE)
    ground.give_card(player, "kards:97th_rifles", Zone.DECK)
    ground.schedule_action(
        ground.add_deck_delay + 610,
        lambda: ground.shuffle_deck(player),
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="步兵第 414 团",
    text="亡计：将 1 张“步兵第 97 团”洗入卡组。抽 3 张牌，对友方总部造成 3 点伤害。",
    art="414th_rifles.png",
    rare=Rarity.NONE,
    at=5,
    df=5,
    operation_cost=1,
    keywords=[DESTRUCTION],
    tags=[CardTag.NOT_IN_START],
    procedures=[
        Procedure(
            DESTRUCTION,
            lambda card, event, ground: event.card is card,
            last_rites,
        )
    ],
)
