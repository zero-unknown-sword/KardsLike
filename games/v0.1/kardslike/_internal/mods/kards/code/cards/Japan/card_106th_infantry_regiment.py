"""步兵第 106 联队"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import (
    BattleGround,
    Card,
    CardData,
    CardTag,
    CardType,
    Country,
    DamageType,
    Event,
    Procedure,
    Zone,
)


def deploy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    部署: 指向一个目标, 对其造成 1 点伤害

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    opponent = event.player.opponent

    def valid(target: Card) -> bool:
        if target is ground.hqs[opponent]:
            return True
        return target.controller is opponent

    ground.request_target(
        event.player,
        card,
        valid,
        lambda target: ground.damage(target, 1, card, DamageType.NONE),
    )


def destroy_action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    亡计: 将一张步兵第 106 联队加入手牌

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.give_card(event.player, "kards:card_106th_infantry_regiment", Zone.HAND)


from mods.kards.code.keywords.deployment import KEYWORD as DEPLOYMENT
from mods.kards.code.keywords.destruction import KEYWORD as DESTRUCTION

from main import Rarity

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.JAPAN,
    cost=2,
    display_name="步兵第 106 联队",
    text="部署：对一个目标造成 1 点伤害。亡计：将一张步兵第 106 联队加入手牌。",
    rare=Rarity.STANDARD,
    at=4,
    df=3,
    operation_cost=1,
    keywords=[DEPLOYMENT, DESTRUCTION],
    tags=[CardTag.NOT_IN_START],
    procedures=[
        Procedure(DEPLOYMENT, lambda card, event, ground: True, deploy_action),
        Procedure(
            DESTRUCTION,
            lambda card, event, ground: ground.turn_owner is not event.player,
            destroy_action,
        ),
    ],
)
