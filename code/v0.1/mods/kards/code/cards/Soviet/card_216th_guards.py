"""近卫步兵第 216 团"""
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
    DamageType,
    Event,
    EventType,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.keywords.countdown import KEYWORD as COUNTDOWN
from mods.kards.code.veteran import VeteranProfile, promote, register_veteran


def countdown_decreased(card: Card, event: Event, ground: BattleGround) -> bool:
    """本单位的倒计时降低"""
    return card.zone is Zone.BOARD and event.card is card


def countdown_payoff(card: Card, event: Event, ground: BattleGround) -> None:
    """倒计时降低: 抽 1 张牌, 对友方总部造成 2 点伤害"""
    player = card.controller
    ground.draw(player, card)
    ground.damage(ground.hqs[player], 2, card, DamageType.NONE)


def countdown_finished(card: Card, event: Event, ground: BattleGround) -> bool:
    """倒计时剩余值为 0"""
    return card.zone is Zone.BOARD and event.card is card and event.dict.get("remaining") == 0


def become_veteran(card: Card, event: Event, ground: BattleGround) -> None:
    """倒计时归零后升为老兵"""
    promote(card, ground)


def veteran_enter_action(card: Card, ground: BattleGround) -> None:
    """升为老兵时, 其他友方单位和总部 +3 防御力"""
    player = card.controller
    for unit in ground.units_in_effect_order(player):
        if unit is not card and unit.controller is player:
            ground.buff(unit, df=3)
    ground.buff(ground.hqs[player], df=3)


BASE_PROCEDURES = [
    Procedure(EventType.COUNTDOWN, countdown_decreased, countdown_payoff),
    Procedure(EventType.COUNTDOWN, countdown_finished, become_veteran),
]

VETERAN = VeteranProfile(
    at=3,
    df=6,
    operation_cost=1,
    art="216th_guards_vet.png",
    text="升为老兵时，使其他友方单位和友方总部获得 +3 防御力。",
    keywords=["guard"],
    base_procedures=BASE_PROCEDURES,
    on_promote=veteran_enter_action,
)

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="近卫步兵第 216 团",
    text="倒计时 2。倒计时降低时，抽 1 张牌并对友方总部造成 2 点伤害；倒计时为 0 时升为老兵。",
    art="216th_guards.png",
    rare=Rarity.STANDARD,
    at=3,
    df=5,
    operation_cost=1,
    keywords=[COUNTDOWN.with_val(2)],
    procedures=BASE_PROCEDURES,
)

register_veteran("kards:card_216th_guards", VETERAN)
