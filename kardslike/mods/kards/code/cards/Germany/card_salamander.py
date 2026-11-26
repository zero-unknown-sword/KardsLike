"""He 162 蝾螈"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[5]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity

from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure, Rarity
from mods.kards.code.keywords.blitz import KEYWORD as BLITZ

CARD_DATA = CardData(
    type=CardType.FIGHTER,
    country=Country.GERMANY,
    cost=4,
    display_name="He 162 蝾螈",
    text="闪击。本单位攻击后，移除自身，下个友方回合开始时返回战场。",
    art="salamander.png",
    rare=Rarity.LIMITED,
    at=1,
    df=2,
    operation_cost=3,
    keywords=[BLITZ],
    procedures=[
        Procedure(
            EventType.ATTACK,
            lambda card, event, ground: event.card is card,
            lambda card, event, ground: _salamander_after_attack(card, ground),
        )
    ],
)

def _salamander_after_attack(card, ground):
    player = card.controller
    line = card.line
    index = line.units.index(card) if line is not None else None
    ground.remove_unit(card, card)

    def back() -> None:
        # 返回战场时优先回到原战线/原位置；绝不回手。
        if line is not None and ground.add_unit(player, card, index=index, line=line):
            return
        if ground.add_unit(player, card):
            return
        if line is not None and line.kind.name == "FRONT":
            if ground.add_unit(player, card, line=ground.support_lines[player]):
                return
        ground.pending_turn_start[player].append(back)

    ground.pending_turn_start[player].append(back)
