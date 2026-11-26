"""扩展德意志帝国研发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardTag, CardType, ChooseOption, Country, Event, EventType, Procedure, Rarity, Zone


def action(card, event, ground):
    player = event.player

    def oil():
        ground.give_card(player, "kards:card_synthetic_oil", Zone.HAND)

    def advanced():
        ground.give_card(player, "kards:card_advanced_reich_rd", Zone.HAND)

    first = Card(type=CardType.ORDER, cost=6, country=Country.GERMANY, name="reich_exp_choose_oil", display_name="扩展德意志帝国研发", text="将 1 张“合成机油”加入手中。", art="reich_exp1.png")
    second = Card(type=CardType.ORDER, cost=6, country=Country.GERMANY, name="reich_exp_choose_advanced", display_name="扩展德意志帝国研发", text="将 1 张“高级德意志帝国研发”加入手中。", art="reich_exp2.png")
    ground.start_choose(player, card, [ChooseOption(first, oil), ChooseOption(second, advanced)])


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=6,
    display_name="扩展德意志帝国研发",
    text="抉择：获取 1 张合成机油，或获取 1 张高级德意志帝国研发。",
    rare=Rarity.STANDARD,
    tags=[CardTag.CHOOSE],
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
