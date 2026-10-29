"""武士之刃"""
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
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """
    目标: 敌方单位

    Args:
        target: 候选目标
        player: 使用方
        ground: 战斗全局参数

    Returns:
        是否合法
    """
    return target.controller is player.opponent


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    消灭指向的敌方单位

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def apply(target: Card) -> None:
        if target is not None:
            ground.kill(target, source=card)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.JAPAN,
    cost=6,
    display_name="武士之刃",
    text="消灭 1 个敌方单位。",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
