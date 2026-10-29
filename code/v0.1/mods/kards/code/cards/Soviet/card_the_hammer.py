"""铁锤"""
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
    DamageType,
    Event,
    EventType,
    Player,
    Procedure,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """
    目标: 任意陆军单位(步兵/炮兵/坦克)

    Args:
        target: 候选目标
        player: 使用方
        ground: 战斗全局参数

    Returns:
        是否合法
    """
    return target.type in (
        CardType.INFANTRY,
        CardType.ARTILLERY,
        CardType.TANK,
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    对指向的陆军造成 6 点非对战伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def apply(target: Card) -> None:
        if target is not None:
            ground.damage(target, 6, DamageType.NONE, card)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=3,
    display_name="铁锤",
    text="对 1 个陆军造成 6 点伤害。",
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
