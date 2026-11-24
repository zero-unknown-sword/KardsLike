"""西里西亚第 44 团"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    COMBAT_KEYWORDS,
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
)
from mods.kards.code.keywords.ambush import KEYWORD as AMBUSH
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    部署时触发

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数

    Returns:
        是否触发
    """
    return event.card is card and event.method is EntryMethod.DEPLOY


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    统计拥有至少 2 个对战词条的友方单位, 每有 1 个抽 1

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数
    """
    player = event.player
    count = 0
    for unit in ground.all_targets():
        if not unit.is_unit or unit.controller is not player:
            continue
        keywords = set(unit.keywords) | set(unit.aura_keywords)
        if len(keywords & COMBAT_KEYWORDS) >= 2:
            count += 1
    for _ in range(min(count, 9)):
        ground.draw(player, card)


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="西里西亚第 44 团",
    text="闪击，伏击。部署：每有 1 个对战词条数不小于 2 的友方单位，抽 1 张牌。",
    art="44th_silesia.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=3,
    operation_cost=1,
    keywords=[BLITZ, AMBUSH],
    procedures=[
        Procedure(
            EventType.USE,
            deployed,
            action,
        )
    ],
)
