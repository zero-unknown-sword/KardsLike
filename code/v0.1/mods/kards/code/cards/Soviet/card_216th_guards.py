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
from mods.kards.code.veteran import VeteranProfile, promote, register_veteran


def friendly_turn_start(card: Card, event: Event, ground: BattleGround) -> bool:
    """友方回合开始时"""
    return (
        card.zone is Zone.BOARD
        and event.player is card.controller
        and not card.has_keyword("veteran")
    )


def turn_start_action(card: Card, event: Event, ground: BattleGround) -> None:
    """付出 2 点总部伤害, 抽一张牌; 第二次后升为老兵"""
    player = card.controller
    ground.damage(ground.hqs[player], 2, card, DamageType.NONE)
    ground.draw(player, card)
    card.veteran_counter = getattr(card, "veteran_counter", 0) + 1
    if card.veteran_counter >= 2:
        promote(card, ground)


def veteran_enter_action(card: Card, ground: BattleGround) -> None:
    """升为老兵时, 其他友方单位和总部 +3 防御力"""
    player = card.controller
    for unit in ground.units_in_effect_order(player):
        if unit is not card and unit.controller is player:
            ground.buff(unit, df=3)
    ground.buff(ground.hqs[player], df=3)


BASE_PROC = Procedure(EventType.TURN_START, friendly_turn_start, turn_start_action)

VETERAN = VeteranProfile(
    at=3,
    df=6,
    operation_cost=1,
    art="216th_guards_vet.png",
    text="升为老兵时，使其他友方单位和友方总部获得 +3 防御力。",
    keywords=["guard"],
    base_procedures=[BASE_PROC],
    on_promote=veteran_enter_action,
)

CARD_DATA = CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=3,
    display_name="近卫步兵第 216 团",
    text="友方回合开始时，对友方总部造成 2 点伤害，抽 1 张牌。第二次后，升为老兵。",
    art="216th_guards.png",
    rare=Rarity.STANDARD,
    at=3,
    df=5,
    operation_cost=1,
    procedures=[BASE_PROC],
)

register_veteran("kards:card_216th_guards", VETERAN)
