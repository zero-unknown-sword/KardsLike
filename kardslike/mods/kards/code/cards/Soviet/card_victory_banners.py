"""胜利旗帜"""
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
    """指向一个单位。"""
    return target.is_unit


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """把目标所有者的单位转换为目标单位。"""
    player = event.player

    def apply(target: Card | None) -> None:
        if target is None:
            return
        owner = target.controller
        for unit in ground.all_targets():
            if unit.controller is owner and unit.is_unit and unit is not target:
                unit.at = target.at
                unit.df = target.df
                unit.max_df = target.max_df

    ground.request_target(player, card, target_valid, apply)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=7,
    display_name="胜利旗帜",
    text="指向 1 个单位。将其所有者的所有单位转换为此单位。",
    art="victory_banners.png",
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
