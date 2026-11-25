"""暴雨(减攻)"""
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
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有敌方单位 -1 AT"""
    player = event.player
    for unit in ground.all_targets():
        if unit.is_unit and unit.controller is not player:
            ground.buff(unit, at=-1)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="暴雨",
    text="所有敌方单位 -1 攻击力。",
    art="deluge_enemy_at.png",
    rare=Rarity.STANDARD,
    sub_type="weather",
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
