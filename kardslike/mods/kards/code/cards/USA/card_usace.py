"""陆军工程兵团"""
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
    指向目标: 己方坦克或步兵

    Args:
        target: 候选目标
        player: 使用方
        ground: 战斗全局参数

    Returns:
        是否合法
    """
    return (
        isinstance(target, Card)
        and target.type in (CardType.INFANTRY, CardType.TANK)
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    指向一个友方坦克或步兵, 使其获得 +1+1

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player

    def valid(target: Card) -> bool:
        return target_valid(target, player, ground)

    def apply(target: Card) -> None:
        if target is not None:
            ground.buff(target, at=1, df=1)

    ground.request_target(player, card, valid, apply)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=0,
    display_name="陆军工程兵团",
    text="使 1 个坦克或步兵获得 +1+1。",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action, target_valid=target_valid)],
)
