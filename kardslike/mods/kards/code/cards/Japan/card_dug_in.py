"""深挖"""
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
    Zone,
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
    对指向单位造成 1 点伤害, 然后将 1 张转变战法洗入卡组

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def apply(target: Card) -> None:
        if not target.is_unit:
            return
        ground.damage(target, 1, card, DamageType.NONE)
        ground.give_card(player, "kards:card_shifting_doctrine", Zone.DECK)
        ground.schedule_action(
            ground.add_deck_delay + 610,
            lambda: ground.shuffle_deck(player),
        )

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
    cost=0,
    display_name="深挖",
    text="对 1 个单位造成 1 点伤害。将 1 张“转变战法”洗入卡组。",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
