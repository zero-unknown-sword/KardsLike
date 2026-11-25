"""皇家西肯特郡团"""
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
    Player,
    Procedure,
    Rarity,
)
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ
from mods.kards.code.keywords.guard import KEYWORD as GUARD


def aura(card: Card, event: Event, ground: BattleGround) -> None:
    """
    其他友方守护单位获得 +2 攻击力和闪击

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in line.units:
            if (
                unit is not card
                and unit.controller is card.controller
                and unit.has_keyword("guard")
            ):
                ground.add_aura(
                    unit,
                    at=2,
                    keyword="blitz",
                    source=card,
                )


CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.BRITAIN,
    cost=4,
    display_name="皇家西肯特郡团",
    text="闪击。守护。其他友方守护单位具有 +2 攻击力和闪击。",
    rare=Rarity.SPECIAL,
    at=4,
    df=4,
    operation_cost=1,
    keywords=[BLITZ, GUARD],
    procedures=[Procedure(EventType.LOOP, lambda card, event, ground: True, aura)],
)
