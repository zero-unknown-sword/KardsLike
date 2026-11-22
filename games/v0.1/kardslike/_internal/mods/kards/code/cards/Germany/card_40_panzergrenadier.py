"""第 40 装甲掷弹兵团"""
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
    EntryMethod,
    Event,
    EventType,
    Player,
    Procedure,
    Rarity,
)

from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.bond import KEYWORD as BOND


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """
    目标: 任意单位

    Args:
        target: 候选目标
        player: 使用方
        ground: 战斗全局参数

    Returns:
        是否合法
    """
    return target.is_unit


def deployed(card: Card, event: Event, ground: BattleGround) -> bool:
    """
    部署时触发, 此时 ENTER 尚未广播

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
    将 1 个单位返回手牌; 若为友方单位则抽 1 张牌

    Args:
        card: 自身
        event: DEPLOY 事件
        ground: 战斗全局参数
    """
    if not any(target.is_unit for target in ground.all_targets()):
        return

    def apply(target: Card) -> None:
        friendly = target.controller is event.player
        ground.return_unit(target, card)
        if friendly:
            ground.draw(event.player, card)

    ground.request_target(
        event.player,
        card,
        lambda target: target_valid(target, event.player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=4,
    display_name="第 40 装甲掷弹兵团",
    text="部署：将 1 个单位返回手牌。若是友方单位，抽 1 张牌。",
    art="40_panzergrenadier.png",
    rare=Rarity.SPECIAL,
    at=3,
    df=3,
    operation_cost=1,
    procedures=[
        Procedure(
            EventType.DEPLOY,
            deployed,
            action,
            target_valid=target_valid,
        )
    ],
    keywords=[BLITZ, BOND]
)
