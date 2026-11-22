"""丛林热"""
import random
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
    EntryMethod,
    Event,
    EventType,
    Player,
    Procedure,
    Rarity,
    cards,
)
from mods.kards.code.keywords.weather import KEYWORD as WEATHER
from mods.kards.code.weather import add_end_cleanup, add_turn_hook, start_climate_choice

def target_valid(target: Card, player: Player, ground: BattleGround) -> bool:
    """目标: 友方单位"""
    return target.is_unit and target.controller is player


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """复制 1 个友方单位到支援阵线并压制"""
    player = event.player

    def apply(target: Card) -> None:
        copy = cards.create(target.card_id)
        if not ground.add_unit(player, copy):
            return
        copy.at = target.at
        copy.df = target.df
        copy.max_df = target.max_df
        copy.keywords = list(target.keywords)
        ground.suppress(copy)

    ground.request_target(
        player,
        card,
        lambda target: target_valid(target, player, ground),
        apply,
    )

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.NEUTRAL,
    cost=4,
    display_name="丛林热",
    text="将 1 个友方单位的复制加入支援阵线。将其压制，直到回合结束。",
    art="jungle_fever_summon.png",
    rare=Rarity.STANDARD,
    keywords=[WEATHER],
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
            target_valid=target_valid,
        )
    ],
)
