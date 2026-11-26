"""白色死神"""
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
    Zone,
)
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """抑制所有敌方单位，并加入一个具有闪击的轻步兵。"""
    player = event.player
    for unit in ground.all_targets():
        if unit.is_unit and unit.controller is not player:
            ground.suppress(unit)
    added = ground.give_card(player, "kards:card_light_infantry", Zone.BOARD)
    if added is not None:
        added.keywords.append("blitz")


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.FINLAND,
    cost=4,
    display_name="白色死神",
    text="抑制所有敌方单位。将 1 个具有闪击的“游击队员”加入支援阵线。",
    art="the_white_death.png",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
