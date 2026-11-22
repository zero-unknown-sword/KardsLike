"""天气与预报的通用逻辑"""
from main import BattleGround, Card, Player, Zone, cards

CLIMATE_IDS: dict[str, str] = {
    "sunny": "kards:card_blue_sky",
    "rain": "kards:card_mist",
    "storm": "kards:card_gale",
}
"""三种基础气象对应的卡牌 id"""

WEATHER_IDS: dict[str, list[str]] = {
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
"""三种气象分别对应的 2K / 4K / 6K 天气卡"""


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
    气象触发后, 选择一张 2K / 4K / 6K 天气, 下个友方回合加入手牌

    Args:
        ground: 战斗全局参数
        player: 玩家
        source: 气象来源
        kind: sunny / rain / storm

    Returns:
        是否成功开始选择
    """
    ids = WEATHER_IDS.get(kind)
    if not ids:
        return False
    choices: list[Card] = []
    for card_id in ids:
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
