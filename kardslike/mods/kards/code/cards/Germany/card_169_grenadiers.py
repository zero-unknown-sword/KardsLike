"""第 169 掷弹兵团"""
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity, Zone


def enemy_order_resolved(card: Card, event: Event, ground: BattleGround) -> bool:
    """敌方指令效果结算完成后"""
    return (
        card.zone is Zone.BOARD
        and event.card is not None
        and event.card.type is CardType.ORDER
        and event.player is card.controller.opponent
    )


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """敌方随机弃 1 张手牌"""
    hand = ground.hands[event.player].cards
    if hand:
        ground.discard_card(event.player, random.choice(hand))


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.GERMANY,
    cost=5,
    display_name="第 169 掷弹兵团",
    text="敌方使用指令后，其随机弃 1 张牌。",
    art="169_grenadiers.png",
    rare=Rarity.ELITE,
    at=5,
    df=6,
    operation_cost=1,
    procedures=[Procedure(EventType.USE_AFTER, enemy_order_resolved, action)],
)
