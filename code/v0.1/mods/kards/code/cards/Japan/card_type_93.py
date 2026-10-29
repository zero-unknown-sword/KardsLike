"""九三式装甲车"""
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


def aura(card: Card, event: Event, ground: BattleGround) -> None:
    """
    其他友方单位获得 +1 攻击力

    Args:
        card: 自身
        event: LOOP 事件
        ground: 战斗全局参数
    """
    if card.controller is None:
        return
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in line.units:
            if unit is not card and unit.controller is card.controller:
                ground.add_aura(unit, at=1, source=card)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.JAPAN,
    cost=1,
    display_name="九三式装甲车",
    text="其他友方单位具有 +1 攻击力。",
    art="type_93.png",
    rare=Rarity.STANDARD,
    at=1,
    df=1,
    operation_cost=1,
    procedures=[Procedure(EventType.LOOP, lambda card, event, ground: True, aura)],
)
