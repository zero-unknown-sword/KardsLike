"""季风雨"""
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
    """双方移除手中或场上花费最高的 2 张卡"""
    for player in (Player.A, Player.B):
        entries: list[Card] = list(ground.hands[player].cards)
        for line in (ground.support_lines[player], ground.front_line):
            entries.extend(item for item in line.units if item.controller is player)
        entries.sort(key=lambda item: item.cost, reverse=True)
        for target in entries[:2]:
            if target in ground.hands[player].cards:
                ground.discard_card(player, target)
            elif target.is_unit and target.zone is Zone.BOARD:
                ground.remove_unit(target, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=6,
    display_name="季风雨",
    text="双方移除手中或场上 2 张花费最高的卡牌。。",
    art="monsoon_rain.png",
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
