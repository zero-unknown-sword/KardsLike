"""天气与预报的通用逻辑"""
import random

from main import BattleGround, Card, Event, EventType, Player, Zone, cards

CLIMATE_IDS: dict[str, str] = {
    "sunny": "kards:card_blue_sky",
    "rain": "kards:card_mist",
    "storm": "kards:card_gale",
}
"""三种基础气象对应的卡牌 id"""

WEATHER_POOL: list[str] = [
    "kards:card_heatwave",
    "kards:card_jungle_fever",
    "kards:card_scorching_sun",
    "kards:card_deluge",
    "kards:card_torrential_rain",
    "kards:card_monsoon_rain",
    "kards:card_thunderstorm",
    "kards:card_tropical_storm",
    "kards:card_cyclone",
]
"""全部天气卡"""


def start_climate_choice(
    ground: BattleGround,
    player: Player,
    source: Card,
) -> bool:
    """
    选择蓝天 / 薄雾 / 狂风之一

    Args:
        ground: 战斗全局参数
        player: 选择方
        source: 效果来源

    Returns:
        是否成功开始选择
    """
    ground.emit(Event(EventType.FORECAST, player=player, source=source))
    choices: list[Card] = []
    for card_id in CLIMATE_IDS.values():
        card = cards.create(card_id)
        card.owner = player
        card.controller = player
        card.zone = Zone.DECK
        choices.append(card)
    return ground.start_card_choice(
        player,
        choices,
        source,
        destination=Zone.HAND,
        title="预报",
    )


def set_weather(ground: BattleGround, player: Player, kind: str) -> None:
    """
    记录玩家当前天气

    Args:
        ground: 战斗全局参数
        player: 玩家
        kind: sunny / rain / storm
    """
    ground.current_weather[player] = kind


def start_forecast(
    ground: BattleGround,
    player: Player,
    source: Card,
) -> bool:
    """
    随机发三张天气, 选择一张, 下个友方回合开始加入手牌

    Args:
        ground: 战斗全局参数
        player: 玩家
        source: 气象来源

    Returns:
        是否成功开始选择
    """
    ground.emit(Event(EventType.FORECAST, player=player, source=source))
    chosen_ids = random.sample(WEATHER_POOL, 3)
    choices: list[Card] = []
    for card_id in chosen_ids:
        card = cards.create(card_id)
        card.owner = player
        card.controller = player
        card.zone = Zone.DECK
        choices.append(card)
    return ground.start_card_choice(
        player,
        choices,
        source,
        destination=Zone.HAND,
        next_turn=True,
        title="预报",
    )
