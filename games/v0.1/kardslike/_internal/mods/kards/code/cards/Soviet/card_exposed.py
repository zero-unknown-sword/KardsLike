"""暴露无遗"""
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
    Rarity,
    has_combat_keyword,
)


def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """
    目标: 没有对战词条的单位

    Args:
        target: 候选目标
        player: 使用方
        ground: 战斗全局参数

    Returns:
        是否合法
    """
    return target.is_unit and not has_combat_keyword(target)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    对没有对战词条的单位造成 5 点伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def apply(target: Card) -> None:
        if target is not None:
            ground.damage(target, 5, DamageType.NONE, card)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=1,
    display_name="暴露无遗",
    text="对 1 个没有对战词条的单位造成 5 点伤害。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
