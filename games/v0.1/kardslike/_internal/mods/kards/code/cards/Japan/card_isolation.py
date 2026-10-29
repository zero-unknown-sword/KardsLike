"""孤立"""
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
    Player,
    Procedure,
    Rarity,
)


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


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    移除目标单位, 在该玩家下个回合开始时返回

    Args:
        card: 孤立
        event: USE 事件
        ground: 战斗全局参数
    """
    def apply(target: Card) -> None:
        if not target.is_unit:
            return
        ground.isolate_card(event.player, target, card)

    ground.request_target(
        event.player,
        card,
        lambda target: target_valid(target, event.player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=1,
    display_name="孤立",
    text="移除 1 个单位，下个友方回合开始时，将其返回战场。",
    art="isolation.png",
    rare=Rarity.ELITE,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
