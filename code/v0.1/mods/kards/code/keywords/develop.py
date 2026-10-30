"""开发"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, KeywordData, Player

KEYWORD = KeywordData(
    name="开发",
    description="从三张构筑外的牌中选择一张加入手牌",
    icon="",
)


def execute(ground: BattleGround, player: Player, source: Card) -> bool:
    """
    执行开发

    Args:
        ground: 战斗全局参数
        player: 玩家
        source: 来源卡牌

    Returns:
        是否成功开始
    """
    return ground.develop_from_pool(player, source)
 