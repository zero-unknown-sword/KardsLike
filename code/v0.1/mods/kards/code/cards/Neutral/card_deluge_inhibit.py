"""暴雨"""
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
    DamageType,
    Event,
    EventType,
    Player,
    PlayerKind,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 任意单位"""
    return target.is_unit


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抑制目标并抽牌"""
    player = event.player

    def apply(target: Card) -> None:
        ground.inhibit_unit(target, card)
        ground.draw(player, card)

    ground.request_target(player, card, lambda target: target_valid(target, player, ground), apply)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="暴雨",
    text="抑制一个单位，抽 1 张牌。预报。",
    art="deluge.png",
    rare=Rarity.STANDARD,
    keywords=[WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
