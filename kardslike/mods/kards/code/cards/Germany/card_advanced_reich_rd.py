"""高级德意志帝国研发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, Rarity

from main import BattleGround, Card, CardTag, CardType, ChooseOption, Country, Event, EventType, Procedure, Rarity, Zone


def action(card, event, ground):
    player = event.player

    def uix():
        ground.give_card(player, "kards:card_uix_submarine", Zone.HAND)

    def uranium():
        ground.give_card(player, "kards:card_uranium_project", Zone.HAND)

    first = Card(type=CardType.ORDER, cost=9, country=Country.GERMANY, name="reich_adv_choose_uix", display_name="高级德意志帝国研发", text="将 1 张“UUIX 级潜艇”加入手中。", art="reich_adv1.png")
    second = Card(type=CardType.ORDER, cost=9, country=Country.GERMANY, name="reich_adv_choose_uranium", display_name="高级德意志帝国研发", text="将 1 张“铀工程”加入手中。", art="reich_adv2.png")
    ground.start_choose(player, card, [ChooseOption(first, uix), ChooseOption(second, uranium)])


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=9,
    display_name="高级德意志帝国研发",
    text="抉择：获取 1 张 UUIX 级潜艇，或获取 1 张铀工程。",
    rare=Rarity.STANDARD,
    tags=[CardTag.CHOOSE],
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
