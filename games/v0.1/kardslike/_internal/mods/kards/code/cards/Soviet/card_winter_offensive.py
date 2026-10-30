"""冬季攻势

KL:
<|使用|>: <源 == 自身> -> /全局. 造成伤害(所有目标, 无类型, 来源自身, 4)\\
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import CardData, CardType, Country, DamageType, EventType, Procedure

from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.SOVIET,
    cost=7,
    display_name="冬季攻势",
    text="对所有目标造成 4 点伤害。",
    rare=Rarity.ELITE,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            lambda card, event, ground: ground.damage(
                ground.targets, 4, card, DamageType.NONE
            ),
        )
    ],
)
