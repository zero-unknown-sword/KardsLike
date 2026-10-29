"""第 18 神射手团"""

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


def deploy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    部署: 将 1 张第 9 神射手团洗入卡组

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.give_card(event.player, "kards:card_9th_bersaglieri", Zone.DECK)
    ground.schedule_action(
        ground.add_deck_delay + 610,
        lambda: ground.shuffle_deck(event.player),
    )


from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.bond import KEYWORD as BOND
from mods.kards.code.keywords.guard import KEYWORD as GUARD
from mods.kards.code.keywords.deployment import KEYWORD as DEPLOYMENT

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.ITALY,
    cost=6,
    display_name="第 18 神射手团",
    text="部署：将 1 张“第 9 神射手团”洗入卡组。",
    rare=Rarity.SPECIAL,
    at=6,
    df=8,
    operation_cost=1,
    keywords=[BLITZ, BOND, GUARD, DEPLOYMENT],
    procedures=[
        Procedure("deployment", lambda card, event, ground: True, deploy_action),
    ],
)
