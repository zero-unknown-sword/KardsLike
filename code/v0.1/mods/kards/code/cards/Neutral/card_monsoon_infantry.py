"""季风雨"""
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
    CardTag,
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

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """友方步兵 +2+2 并再次行动"""
    player = event.player
    for unit in ground.all_targets():
        if not unit.is_unit or unit.controller is not player:
            continue
        if unit.type is not CardType.INFANTRY:
            continue
        ground.buff(unit, at=2, df=2)
        unit.attacks_turn = 0
        unit.remove_tag(CardTag.MOVED)
        unit.remove_tag(CardTag.ATTACKED)
        unit.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="季风雨",
    text="所有友方步兵 +2 攻击力，+2 防御力，并能再次行动。预报。",
    art="monsoon_infantry.png",
    rare=Rarity.STANDARD,
    keywords=[WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
