"""热带风暴"""
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
    """双方洗回手牌并抽取同等数量"""
    counts: dict[Player, int] = {}
    for player in (Player.A, Player.B):
        count = len(list(ground.hands[player].cards))
        counts[player] = count
        for item in list(ground.hands[player].cards):
            ground.put_card_into_deck(player, item)
    maximum = max(counts.values(), default=0)
    for player in (Player.A, Player.B):
        for _ in range(maximum):
            ground.draw(player, card)
    start_climate_choice(ground, event.player, card)

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="热带风暴",
    text="双方将所有手牌洗入卡组，抽取等同于最大洗入数量的卡牌。预报。",
    art="tropical_storm.png",
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
