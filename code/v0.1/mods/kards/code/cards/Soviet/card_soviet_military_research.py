"""苏联军事研发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardTag,
    CardData,
    CardType,
    ChooseOption,
    Country,
    Event,
    EventType,
    Procedure,
    Rarity,
    Zone,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抉择：获取气动雪橇或扩展苏联研发"""
    player = event.player

    def aerosani() -> None:
        ground.give_card(player, "kards:card_aerosani", Zone.HAND)

    def expanded() -> None:
        ground.give_card(player, "kards:card_expanded_soviet_research", Zone.HAND)

    first = Card(
        type=CardType.ORDER,
        cost=3,
        country=Country.SOVIET,
        name="research_choose_aerosani",
        display_name="苏联军事研发",
        text="将 1 张“气动雪橇”加入手中。",
        art="card_a_choose1.png",
    )
    second = Card(
        type=CardType.ORDER,
        cost=3,
        country=Country.SOVIET,
        name="research_choose_expanded",
        display_name="苏联军事研发",
        text="将 1 张“扩展苏联研发”加入手中。",
        art="card_a_choose2.png",
    )
    ground.start_choose(
        player,
        card,
        [
            ChooseOption(first, aerosani),
            ChooseOption(second, expanded),
        ],
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=3,
    display_name="苏联军事研发",
    text="抉择：获取 1 张气动雪橇，或获取 1 张扩展苏联研发。",
    art="soviet_military_research.png",
    rare=Rarity.ELITE,
    tags=[CardTag.CHOOSE],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
