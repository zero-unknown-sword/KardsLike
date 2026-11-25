"""海联队"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, DamageType, Event, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 对敌方总部造成 2 点伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.damage(ground.hqs[event.player.opponent], 2, card, DamageType.NONE)


from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.JAPAN,
    cost=5,
    display_name="海联队",
    text="闪击。亡计：对敌方总部造成 2 点伤害。",
    rare=Rarity.STANDARD,
    at=3,
    df=3,
    operation_cost=0,
    keywords=[BLITZ, DESTRUCTION],
    procedures=[Procedure(DESTRUCTION, lambda card, event, ground: True, action)],
)
