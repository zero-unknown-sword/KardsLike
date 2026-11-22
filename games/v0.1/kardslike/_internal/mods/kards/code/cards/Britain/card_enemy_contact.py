"""逢敌"""
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
    压制 1 个单位并抽 1 张牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def apply(target: Card) -> None:
        if target is not None:
            ground.suppress(target)
            # 手牌已满时不再抽牌, 避免爆牌
            if len(ground.hands[player].cards) < ground.hands[player].MAX_CARDS:
                ground.draw(player, card)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.BRITAIN,
    cost=2,
    display_name="逢敌",
    text="压制 1 个单位。抽 1 张牌。",
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
