"""KARDS 部署兜底流程。

部署流程固定为：
部署效果 -> 协力 -> 进入战场
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, DEPLOY_FALLBACK_HOOKS, Player


def resolve_bond(ground: BattleGround, player: Player, card: Card) -> None:
    """在部署效果之后结算协力。

    Args:
        ground: 战斗全局参数
        player: 部署方
        card: 刚部署的单位
    """
    ground.check_bond(player, card)


if resolve_bond not in DEPLOY_FALLBACK_HOOKS:
    DEPLOY_FALLBACK_HOOKS.append(resolve_bond)
