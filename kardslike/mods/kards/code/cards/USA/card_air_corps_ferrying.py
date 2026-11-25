"""航空兵团运输"""
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
    """目标: 友方单位"""
    return target.is_unit and target.controller is player


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """剩余指挥点不小于 5 时全体 +1+1，否则单个友方单位 +1+1"""
    player = event.player
    if ground.kredits[player].credits >= 5:
        for unit in ground.all_targets():
            if unit.is_unit and unit.controller is player:
                ground.buff(unit, at=1, df=1)
        return

    def apply(target: Card) -> None:
        ground.buff(target, at=1, df=1)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.USA,
    cost=1,
    display_name="航空兵团运输",
    text="使 1 个友方单位获得 +1+1。若剩余指挥点数不小于 5，改为使所有友方单位获得 +1+1。",
    art="air_corps_ferrying.png",
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
