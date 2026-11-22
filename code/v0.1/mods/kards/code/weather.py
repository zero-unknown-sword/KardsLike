"""天气与预报的通用逻辑"""
import random

from main import BattleGround, Card, Event, EventType, Player, Zone, cards

CLIMATE_IDS: dict[str, str] = {
    "sunny": "kards:card_blue_sky",
    "rain": "kards:card_mist",
    "storm": "kards:card_gale",
}
"""三种基础气象对应的卡牌 id"""

CLIMATE_SLOTS: dict[str, list[str]] = {
    "sunny": [
        "kards:card_heatwave",
        "kards:card_jungle_fever",
        "kards:card_scorching_sun",
    ],
    "rain": [
        "kards:card_deluge",
        "kards:card_torrential_rain",
        "kards:card_monsoon_rain",
    ],
    "storm": [
        "kards:card_thunderstorm",
        "kards:card_tropical_storm",
        "kards:card_cyclone",
    ],
}
"""每种气象固定三个槽位"""

WEATHER_VARIANTS: dict[str, list[str]] = {
    "kards:card_heatwave": ["kards:card_heatwave"],
    "kards:card_jungle_fever": ["kards:card_jungle_fever"],
    "kards:card_scorching_sun": ["kards:card_scorching_sun"],
    "kards:card_deluge": ["kards:card_deluge"],
    "kards:card_torrential_rain": ["kards:card_torrential_rain"],
    "kards:card_monsoon_rain": ["kards:card_monsoon_rain"],
    "kards:card_thunderstorm": ["kards:card_thunderstorm"],
    "kards:card_tropical_storm": ["kards:card_tropical_storm"],
    "kards:card_cyclone": ["kards:card_cyclone"],
}
"""同名天气的变体池, 后续每项补足 3 张"""


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
    kind: str,
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
    slots = CLIMATE_SLOTS.get(kind)
    if not slots:
        return False
    chosen_ids = [
        random.choice(WEATHER_VARIANTS[card_id])
        for card_id in slots
    ]
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
