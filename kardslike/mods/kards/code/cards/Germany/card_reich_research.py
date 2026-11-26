"""德意志帝国研发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardTag, CardType, ChooseOption, Country, Event, EventType, Procedure, Rarity, Zone


def action(card, event, ground):
    player = event.player

    def v1():
        ground.give_card(player, "kards:card_v1_flying_bomb", Zone.HAND)

    def expanded():
        ground.give_card(player, "kards:card_expanded_reich_rd", Zone.HAND)

    first = Card(type=CardType.ORDER, cost=3, country=Country.GERMANY, name="reich_choose_v1", display_name="德意志帝国研发", text="将 1 张“V-1 飞行炸弹”加入手中。", art="reich_choose1.png")
    second = Card(type=CardType.ORDER, cost=3, country=Country.GERMANY, name="reich_choose_expanded", display_name="德意志帝国研发", text="将 1 张“扩展德意志帝国研发”加入手中。", art="reich_choose2.png")
    ground.start_choose(player, card, [ChooseOption(first, v1), ChooseOption(second, expanded)])


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=3,
    display_name="德意志帝国研发",
    text="抉择：获取 1 张 V-1 飞行炸弹，或获取 1 张扩展德意志帝国研发。",
    rare=Rarity.ELITE,
    tags=[CardTag.CHOOSE],
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
