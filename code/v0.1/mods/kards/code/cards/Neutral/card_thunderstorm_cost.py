"""雷暴"""
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
    Event,
    EventType,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """随机改变双方手牌费用"""
    player = event.player
    enemy_hand = ground.hands[player.opponent].cards
    if enemy_hand:
        random.choice(enemy_hand).apply_permanent(cost=1)
    own_hand = ground.hands[player].cards
    if own_hand:
        random.choice(own_hand).apply_permanent(cost=-1)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="雷暴",
    text="随机使 1 张敌方手牌获得 +1 花费，随机使 1 张友方卡牌获得 -1 花费。",
    art="thunderstorm_cost.png",
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
