"""Sd Kfz 10 PaK 38"""
import sys
from pathlib import Path
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

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
)


def on_buff(card: Card, event: Event, ground: BattleGround) -> None:
    """
    其他卡牌增加攻击力时, 自身获得 +1 攻击力直到回合结束

    Args:
        card: 自身
        event: BUFF 事件
        ground: 战斗全局参数
    """
    target = event.dict.get("target")
    source = event.dict.get("source")
    at = event.dict.get("at", 0)
    if (
        isinstance(target, Card)
        and target is card
        and isinstance(source, Card)
        and source is not card
        and isinstance(at, int)
        and at > 0
    ):
        card.add_temporary_at(1)


CARD_DATA = CardData(
    type=CardType.TANK,
    country=Country.GERMANY,
    cost=1,
    display_name="Sd Kfz 10 PaK 38",
    text="因其他卡牌增加攻击力时，具有 +1 攻击力，直到回合结束。此效果可叠加。",
    art="sd_kfz_10_pak_38.png",
    rare=Rarity.STANDARD,
    at=1,
    df=3,
    operation_cost=1,
    procedures=[Procedure(EventType.BUFF, lambda card, event, ground: True, on_buff)],
    keywords=[BLITZ]
)
