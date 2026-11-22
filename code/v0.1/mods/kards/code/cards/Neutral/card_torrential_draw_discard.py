"""骤雨"""
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

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抽 3 再弃 1"""
    player = event.player
    for _ in range(3):
        ground.draw(player, card)

    def discard_selected(selected: list[Card]) -> None:
        for item in selected:
            ground.discard_card(player, item)

    hand = ground.hands[player].cards
    if not hand:
        return
    if ground.kind_of(player) is PlayerKind.AI:
        discard_selected([random.choice(hand)])
        return
    ground.start_selection(
        player,
        1,
        1,
        discard_selected,
        title="弃 1 张牌",
    )

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="骤雨",
    text="抽 3 张牌，选择并弃 1 张。预报。",
    art="torrential_draw_discard.png",
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
