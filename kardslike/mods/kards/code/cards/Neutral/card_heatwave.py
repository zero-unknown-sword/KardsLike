"""热浪"""
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
    Player,
    Procedure,
    Rarity,
    Zone,
)
from mods.kards.code.weather import add_turn_hook, start_climate_choice

def action(card: Card, event: Event, ground: BattleGround) -> None:
    """所有陆军 +2 攻击力, 空军 +3 攻击力, 持续到回合结束"""
    player = event.player

    def amount_for(unit: Card) -> int:
        return 2 if unit.type in (CardType.INFANTRY, CardType.TANK, CardType.ARTILLERY) else 3

    def apply_aura(event: Event, ground: BattleGround) -> None:
        for unit in ground.all_targets():
            if unit.is_unit:
                ground.add_aura(unit, at=amount_for(unit), source=card)

    # 与西肯特郡团相同的持续光环, 新入场单位下一帧自然获得
    apply_aura(event, ground)
    add_turn_hook(ground, player, EventType.LOOP, apply_aura)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=2,
    display_name="热浪",
    text="所有陆军 +2 攻击力，空军 +3 攻击力，直到回合结束。",
    art="heatwave.png",
    rare=Rarity.STANDARD,
    sub_type="weather",
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
