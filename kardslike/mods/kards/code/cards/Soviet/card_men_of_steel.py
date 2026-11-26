"""钢铁之躯"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有友方单位获得 +1 重甲。"""
    for unit in ground.all_targets():
        if unit.is_unit and unit.controller is event.player:
            unit.armor = min(3, unit.armor + 1)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=1,
    display_name="钢铁之躯",
    text="抉择：使所有友方单位获得 +1 重甲，或将 1 张“铁锤”加入手牌。",
    art="men_of_steel.png",
    rare=Rarity.SPECIAL,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
