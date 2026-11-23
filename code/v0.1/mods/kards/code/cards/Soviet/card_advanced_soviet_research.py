"""高级苏联研发"""
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
    """抉择：获取倾斜装甲，或 3 张斯大林管风琴"""
    player = event.player

    def armor() -> None:
        ground.give_card(player, "kards:card_sloped_armor", Zone.HAND)

    def organs() -> None:
        for _ in range(3):
            ground.give_card(player, "kards:card_stalins_organ", Zone.HAND)

    armor_card = Card(
        type=CardType.ORDER,
        cost=9,
        country=Country.SOVIET,
        name="advanced_choose_armor",
        display_name="高级苏联研发",
        text="将 1 张“倾斜装甲”加入手中。",
        art="card_advanced_choose1.png",
    )
    organ_card = Card(
        type=CardType.ORDER,
        cost=9,
        country=Country.SOVIET,
        name="advanced_choose_organs",
        display_name="高级苏联研发",
        text="将 3 张“斯大林管风琴”加入手中。",
        art="card_advanced_choose2.png",
    )
    ground.start_choose(
        player,
        card,
        [
            ChooseOption(armor_card, armor),
            ChooseOption(organ_card, organs),
        ],
    )


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=9,
    display_name="高级苏联研发",
    text="抉择：获取 1 张倾斜装甲，或获取 3 张斯大林管风琴。",
    art="advanced_soviet_research.png",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
