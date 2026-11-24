"""老兵机制

老兵是 KARDS mod 内的特殊机制, 不进入 main 的核心规则:
卡牌本身注册老兵档案, 满足条件时调用 promote 进行升阶。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from main import BattleGround, Card, EventType, MAX_STAT, Procedure


@dataclass
class VeteranProfile:
    """老兵档案

    Attributes:
        at: 老兵攻击力
        df: 老兵防御力
        operation_cost: 老兵行动花费
        art: 老兵卡图
        text: 老兵卡面文本
        keywords: 老兵基础关键词
        procedures: 老兵基础效果
        base_procedures: 升级前的基础效果, 用于区分外部赋予的效果
        base_keywords: 升级前的基础关键词
        base_tags: 升级前的基础标签
        on_promote: 升为老兵时额外执行的效果
    """

    at: int
    df: int
    operation_cost: int
    art: str
    text: str = ""
    keywords: list[str] = field(default_factory=list)
    procedures: list[Procedure] = field(default_factory=list)
    base_procedures: list[Procedure] = field(default_factory=list)
    base_keywords: list[str] = field(default_factory=list)
    base_tags: list[str] = field(default_factory=list)
    on_promote: Callable[[Card, BattleGround], None] | None = None


VETERANS: dict[str, VeteranProfile] = {}


def register_veteran(card_id: str, profile: VeteranProfile) -> None:
    """注册一张卡牌的老兵档案。

    Args:
        card_id: 卡牌 id
        profile: 老兵档案
    """
    VETERANS[card_id] = profile


def promote(card: Card, ground: BattleGround) -> bool:
    """将单位升为老兵。

    只替换单位自身的基础数据与基础效果, 保留其他卡牌赋予的
    永久属性、临时关键词、外部效果和光环。

    Args:
        card: 要升级的单位
        ground: 战斗全局参数

    Returns:
        是否成功升级
    """
    profile = VETERANS.get(card.card_id)
    if profile is None or not card.is_unit or card.has_keyword("veteran"):
        return False

    old_base_keywords = set(card.base_keywords)
    old_base_tags = set(card.base_tags)
    external_keywords = [keyword for keyword in card.keywords if keyword not in old_base_keywords]
    external_tags = set(card.tags) - old_base_tags
    external_procedures = [p for p in card.procedures if p not in profile.base_procedures]
    aura_at = card.aura_at
    aura_keywords = set(card.aura_keywords)
    operation_cost_delta = card.operation_cost - card.initial_operation_cost

    card.clear_auras()
    card.initial_at = profile.at
    card.initial_df = profile.df
    card.initial_operation_cost = profile.operation_cost
    card.base_keywords = [*profile.keywords, "veteran"]
    card.base_tags = list(profile.base_tags)
    card.base_procedures = list(profile.procedures)
    card.procedures = [*profile.procedures, *external_procedures]
    card.keywords = list(dict.fromkeys([*card.base_keywords, *external_keywords]))
    card.aura_keywords = aura_keywords
    card.tags = set(card.base_tags) | external_tags
    card.art = profile.art
    card.text = profile.text
    card.aura_at = aura_at
    card.at = min(MAX_STAT, profile.at + card.at_bonus + aura_at)
    card.df = min(MAX_STAT, profile.df + card.df_bonus)
    card.max_df = card.df
    card.operation_cost = profile.operation_cost + operation_cost_delta
    if profile.on_promote is not None:
        profile.on_promote(card, ground)
    return True


def veteran_procedure(
    profile: VeteranProfile,
    trigger: EventType,
    condition: Callable[[Card, "Event", BattleGround], bool],
) -> Procedure:
    """创建一个满足条件后升为老兵的基础效果。

    Args:
        profile: 老兵档案
        trigger: 触发事件
        condition: 触发条件

    Returns:
        升级流程
    """

    def action(card: Card, event: "Event", ground: BattleGround) -> None:
        promote(card, ground)

    return Procedure(trigger, condition, action)
