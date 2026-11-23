"""扩展苏联研发"""
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
    ChooseOption,
    Country,
    Event,
    EventType,
    Procedure,
    Rarity,
    Zone,
    cards,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抉择：获取标准弹药或高级苏联研发"""
    player = event.player

    def standard() -> None:
        ground.give_card(player, "kards:card_standard_ammo", Zone.HAND)

    def advanced() -> None:
        ground.give_card(player, "kards:card_advanced_soviet_research", Zone.HAND)

    standard_card = Card(
        type=CardType.ORDER,
        cost=6,
        country=Country.SOVIET,
        name="expanded_choose_standard",
        display_name="扩展苏联研发",
        text="将 1 张“标准弹药”加入手中。",
        art="card_expanded_choose1.png",
    )
    advanced_card = Card(
        type=CardType.ORDER,
        cost=6,
        country=Country.SOVIET,
        name="expanded_choose_advanced",
        display_name="扩展苏联研发",
        text="将 1 张“高级苏联研发”加入手中。",
        art="card_expanded_choose2.png",
    )
    ground.start_choose(
        player,
        card,
        [
            ChooseOption(standard_card, standard),
            ChooseOption(advanced_card, advanced),
        ],
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=6,
    display_name="扩展苏联研发",
    text="抉择：获取 1 张标准弹药，或获取 1 张高级苏联研发。",
    art="expanded_soviet_research.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
