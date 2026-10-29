"""反潜巡逻"""
import random
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


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    获得 3 个指挥点槽, 若盟国为美国则随机消灭 1 个敌方单位

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    player = event.player
    ground.kredits[player].add_slots(3)  # 获得指挥点槽
    if ground.config.host_ally is not Country.USA and player is Player.A:
        return
    if ground.config.guest_ally is not Country.USA and player is Player.B:
        return
    enemy_units = [
        unit
        for line in (
            ground.support_lines[player.opponent],
            ground.front_line,
        )
        for unit in line.units
        if unit.controller is player.opponent
    ]
    if enemy_units:
        target = random.choice(enemy_units)
        card.destroy(target, ground)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=7,
    display_name="反潜巡逻",
    text="额外获得 3 个指挥点槽。若美国是盟国，随机消灭 1 个敌方单位。",
    rare=Rarity.LIMITED,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
