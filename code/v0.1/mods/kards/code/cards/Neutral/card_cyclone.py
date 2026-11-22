"""旋风"""
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
    Rarity,
    Zone,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抽 3 张牌, 对友方总部造成手牌数伤害"""
    player = event.player
    for _ in range(3):
        ground.draw(player, card)
    ground.damage(
        ground.hqs[player],
        len(ground.hands[player].cards),
        card,
        DamageType.NONE,
    )

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="旋风",
    text="抽 3 张牌，对友方总部造成等同于手牌数的伤害。预报。",
    art="cyclone.png",
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
