"""第 9 神射手团"""

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
    Zone,
)


def destroy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 将 1 张第 18 神射手团洗入卡组

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.give_card(event.player, "kards:card_18th_bersaglieri", Zone.DECK)
    ground.schedule_action(
        ground.add_deck_delay + 610,
        lambda: ground.shuffle_deck(event.player),
    )


from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.bond import KEYWORD as BOND

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.ITALY,
    cost=5,
    display_name="第 9 神射手团",
    text="亡计：将 1 张“第 18 神射手团”洗入卡组。",
    rare=Rarity.STANDARD,
    at=5,
    df=6,
    operation_cost=1,
    keywords=[DESTRUCTION, BLITZ, BOND],
    procedures=[
        Procedure(DESTRUCTION, lambda card, event, ground: True, destroy_action),
    ],
)
