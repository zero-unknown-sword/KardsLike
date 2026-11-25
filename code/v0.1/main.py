"""
main.py

游戏主程序
"""
from __future__ import annotations

# cSpell:ignore usace
import logging
import math
import random
import sys
import json
import time
import textwrap

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum, auto
from pathlib import Path
from typing import TYPE_CHECKING, cast, Any, Callable, TypedDict, Final

import pygame

from pygame import Surface
from pygame.event import Event
from pygame.font import Font
from pygame.time import Clock

# 保证以文件方式启动时也能导入同目录的 tools 与 mods
_PACKAGE_ROOT = str(Path(__file__).resolve().parent)
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from tools import BetterLogger, Button, ButtonGroup, Color, CrashReporter, ImageLoader, IntAttr, LogManager

# 让动态加载的卡牌文件能通过 import main 拿到当前模块(避免重复导入)
sys.modules["main"] = sys.modules[__name__]

# tools 已把 logging 的记录器类替换为支持 trace 的 BetterLogger
logger = cast(BetterLogger, logging.getLogger("kardslike"))

MAX_STAT: Final[int] = 99
MAX_HQ_DF: Final[int] = 99
BATTLE_EN: Final[str] = "Battle (TBD)"
"""战斗的英文名暂定"""
"""攻击力/防御力数值上限"""


def _string_dict(value: Any) -> dict[str, Any]:
    """
    把 JSON 对象转换为只含字符串键的字典

    Args:
        value: 待转换对象

    Returns:
        字符串键字典
    """
    if not isinstance(value, dict):
        return {}
    mapping = cast(dict[object, object], value)
    result: dict[str, Any] = {}
    for key, item in mapping.items():
        if isinstance(key, str):
            result[key] = item
    return result


def _object_list(value: Any) -> list[object]:
    """把 JSON 数组转换为 object 列表"""
    if not isinstance(value, list):
        return []
    return cast(list[object], value)

# ==================== 枚举 ====================


class Player(StrEnum):
    """
    对战双方

    Attributes:
        A: 玩家 A
        B: 玩家 B
    """
    A = auto()
    """玩家 A"""
    B = auto()
    """玩家 B"""

    @property
    def opponent(self) -> "Player":
        """返回对手"""
        return Player.B if self is Player.A else Player.A


class LineKind(StrEnum):
    """
    战线种类

    Attributes:
        FRONT: 前线
        SUPPORT: 支援阵线
    """
    FRONT = auto()
    """前线"""
    SUPPORT = auto()
    """支援阵线"""


class Country(StrEnum):
    """
    卡牌所属国家

    Attributes:
        ANZAC: 澳新军团
        BRITAIN: 英国
        FINLAND: 芬兰
        FRANCE: 法国
        GERMANY: 德国
        ITALY: 意大利
        JAPAN: 日本
        NEUTRAL: 中立
        POLAND: 波兰
        SOVIET: 苏联
        USA: 美国
    """
    ANZAC = auto()
    """澳新军团"""
    BRITAIN = auto()
    """英国"""
    FINLAND = auto()
    """芬兰"""
    FRANCE = auto()
    """法国"""
    GERMANY = auto()
    """德国"""
    ITALY = auto()
    """意大利"""
    JAPAN = auto()
    """日本"""
    NEUTRAL = auto()
    """中立"""
    POLAND = auto()
    """波兰"""
    SOVIET = auto()
    """苏联"""
    USA = auto()
    """美国"""


class Rarity(StrEnum):
    """
    卡牌稀有度

    Attributes:
        STANDARD: 标准
        LIMITED: 铜卡
        SPECIAL: 银卡
        ELITE: 金卡
        NONE: 无稀有度, 衍生牌
    """
    STANDARD = "standard"
    LIMITED = "limited"
    SPECIAL = "special"
    ELITE = "elite"
    """金卡 (精英)"""
    NONE = "none"
    """无稀有度, 用于衍生牌"""


class CardType(StrEnum):
    """
    卡牌类型

    单位不是单独的类型, 而是步兵/坦克/战斗机/轰炸机/火炮五种类型的统称

    Attributes:
        INFANTRY: 步兵
        TANK: 坦克
        FIGHTER: 战斗机
        BOMBER: 轰炸机
        ARTILLERY: 火炮
        ORDER: 指令
        COUNTERMEASURE: 反制
        HQ: 总部
    """
    INFANTRY = auto()
    """步兵"""
    TANK = auto()
    """坦克"""
    FIGHTER = auto()
    """战斗机"""
    BOMBER = auto()
    """轰炸机"""
    ARTILLERY = auto()
    """火炮"""
    ORDER = auto()
    """指令"""
    COUNTERMEASURE = auto()
    """反制"""
    HQ = auto()
    """总部"""

    @property
    def is_unit(self) -> bool:
        """
        是否为单位的五种类型之一

        Returns:
            是否为步兵/坦克/战斗机/轰炸机/火炮
        """
        return self in (
            CardType.INFANTRY,
            CardType.TANK,
            CardType.FIGHTER,
            CardType.BOMBER,
            CardType.ARTILLERY,
        )


class DamageType(StrEnum):
    """
    伤害类型

    对抗伤害包含对战伤害(反击/攻击)、战斗伤害与对总部的攻击伤害
    其他伤害不属于对抗伤害

    Attributes:
        COUNTER: 反击伤害, 属于对战伤害
        ATTACK: 单位攻击伤害, 属于对战伤害
        BATTLE: 战斗伤害, 由特殊的战斗触发(英文暂定 Battle (TBD))
        HQ_ATTACK: 对总部的攻击伤害, 属于对抗伤害但不属于对战伤害
        OTHER: 其他伤害, 不属于对抗伤害
        NONE: 无类型伤害, 由卡牌效果直接造成
        MORALE: 士气伤害, 卡组抽空时受到
    """
    COUNTER = auto()
    """反击伤害, 单位受到攻击时对攻击者造成, 属于对战伤害"""
    ATTACK = auto()
    """单位攻击伤害, 属于对战伤害"""
    BATTLE = auto()
    """战斗伤害, 由特殊的战斗触发"""
    HQ_ATTACK = auto()
    """对总部造成的攻击伤害, 属于对抗伤害但不属于对战伤害"""
    OTHER = auto()
    """其他伤害, 不属于对抗伤害"""
    NONE = auto()
    """无类型伤害, 由卡牌效果直接造成"""
    MORALE = auto()
    """士气伤害, 卡组抽空时受到"""

    @property
    def is_confrontation(self) -> bool:
        """
        是否为对抗伤害

        Returns:
            是否属于对抗伤害
        """
        return self not in (DamageType.OTHER, DamageType.NONE, DamageType.MORALE)

    @property
    def is_duel(self) -> bool:
        """
        是否为对战伤害

        Returns:
            是否属于对战伤害
        """
        return self in (DamageType.COUNTER, DamageType.ATTACK)


class Zone(StrEnum):
    """
    卡牌所处区域

    Attributes:
        DECK: 卡组
        HAND: 手牌
        BOARD: 场上
        DISCARD: 弃牌堆
        REMOVED: 移除区
    """
    DECK = auto()
    """卡组"""
    HAND = auto()
    """手牌"""
    BOARD = auto()
    """场上"""
    DISCARD = auto()
    """弃牌堆"""
    REMOVED = auto()
    """移除区"""


class CardTag(StrEnum):
    """
    卡牌标签, 控制运行时的临时状态

    Attributes:
        CANNOT_ACT_WHEN_ENTER: 进入战场的当回合无法行动
        CANNOT_MOVE: 无法移动
        CANNOT_ATTACK: 无法攻击
        CANNOT_BE_ATTACKED: 无法被攻击
        MOVED: 本回合已经移动过
        ATTACKED: 本回合已经攻击过
        DAMAGE_CAP_ONE: 受到的对战伤害至多为 1
        OVERFLOW_DAMAGE: 攻击消灭单位时溢出伤害转移至敌方总部
        REFRESH_ON_KILL: 攻击消灭单位后重置行动状态
        IGNORE_RESET: 离开/进入战场时不重置状态
        HQ_IMMUNE_ENEMY_TURN: 敌方回合中友方总部免疫
        SLAM_UP_1: 拍桌等级提升 1 级: 小 -> 中
        SLAM_UP_2: 拍桌等级提升 2 级: 小 -> 大
        NOT_IN_START: 构筑外, 不参与初始卡组构筑
        SPECIAL_SOURCE: 回合开始抽牌等系统行为的特殊来源
    """
    CANNOT_ACT_WHEN_ENTER = "CANNOT_ACT_WHEN_ENTER"
    """进入战场的当回合无法行动"""
    CANNOT_MOVE = "CANNOT_MOVE"
    """无法移动"""
    CANNOT_ATTACK = "CANNOT_ATTACK"
    """无法攻击"""
    CANNOT_BE_ATTACKED = "CANNOT_BE_ATTACKED"
    """无法被攻击"""
    MOVED = "MOVED"
    """本回合已经移动过"""
    ATTACKED = "ATTACKED"
    """本回合已经攻击过"""
    DAMAGE_CAP_ONE = "DAMAGE_CAP_ONE"
    """受到的对战伤害至多为 1"""
    OVERFLOW_DAMAGE = "OVERFLOW_DAMAGE"
    """攻击消灭单位时, 溢出伤害转移至敌方总部"""
    REFRESH_ON_KILL = "REFRESH_ON_KILL"
    """攻击消灭单位后重置行动状态"""
    IGNORE_RESET = "IGNORE_RESET"
    """离开/进入战场时不重置状态"""
    HQ_IMMUNE_ENEMY_TURN = "HQ_IMMUNE_ENEMY_TURN"
    """敌方回合中, 友方总部具有免疫"""
    SLAM_UP_1 = "SLAM_UP_1"
    """拍桌等级提升 1 级"""
    SLAM_UP_2 = "SLAM_UP_2"
    """拍桌等级提升 2 级"""
    NOT_IN_START = "NOT_IN_START"
    """构筑外, 不参与初始卡组构筑(TODO: 名称待定)"""
    CHOOSE = "CHOOSE"
    """使用前需要抉择: 预览不扣费, 结算后才支付"""
    SPECIAL_SOURCE = "SPECIAL_SOURCE"
    """系统特殊来源"""
    IN_START = "IN_START"
    """构筑内卡牌"""
    KEEP_SHOCK = "KEEP_SHOCK"
    """不会失去冲击"""
    UNINHIBITABLE = "UNINHIBITABLE"
    """不能被抑制"""
    DEFENSE_FLOOR_ONE = "DEFENSE_FLOOR_ONE"
    """防御力不会被降到 1 以下"""


class EntryMethod(StrEnum):
    """
    单位进入战场的方式

    Attributes:
        DEPLOY: 从手牌部署
        ADD: 由效果加入
    """
    DEPLOY = "DEPLOY"
    """从手牌部署"""
    ADD = "ADD"
    """由效果加入"""


class LeaveMethod(StrEnum):
    """
    单位离开战场的方式

    Attributes:
        DESTROYED: 被消灭
        REMOVED: 被移除
        RETURN_HAND: 返回手牌
    """
    DESTROYED = "DESTROYED"
    """被消灭"""
    REMOVED = "REMOVED"
    """被移除, 非消灭方式离开战场"""
    RETURN_HAND = "RETURN_HAND"
    """返回手牌"""


class PlayerKind(StrEnum):
    """
    玩家类型

    Attributes:
        HUMAN: 本地真人
        AI: 电脑
        REMOTE: 联机对手
    """
    HUMAN = auto()
    """本地真人"""
    AI = auto()
    """电脑"""
    REMOTE = auto()
    """联机对手"""

# ==================== 事件与效果 ====================


class EventType(IntEnum):
    """
    事件类型, 使用 pygame 自定义事件编号, 作为 Procedure.trigger 与 Event.type 使用

    Attributes:
        BATTLE_START: 战斗开始
        DRAW: 抽牌
        USE: 使用卡牌
        PLAY: USE 的别名
        MOVE: 单位移动
        ATTACK: 单位攻击
        DAMAGED: 受到伤害
        LEAVE: 单位离开战场
        ENTER: 单位进入场上
        ADD_TO_HAND: 将卡牌加入手牌
        ADD_TO_DECK: 将卡牌加入卡组
        ADD_TO_BOARD: 将卡牌加入场上
        LOOP: 每帧触发的循环事件
        TURN_START: 回合开始
        TURN_END: 回合结束
        DISCARD: 卡牌被弃掉
        SHUFFLE: 卡组洗切
        INTEL_OVERFLOW: 情报溢出
        DEVELOP: 开发选取
        LOOT: 战利品选取
        BUFF: 属性增加
    """
    BATTLE_START = pygame.event.custom_type()
    """
    战斗开始, 同时投递到 pygame 事件队列并经 emit 广播

    数据:
        host: 主端玩家类型
        guest: 客端玩家类型
        host_country: 主端主国
        guest_country: 客端主国
        host_ally: 主端盟国
        guest_ally: 客端盟国
        host_deck: 主端卡组 id 列表
        guest_deck: 客端卡组 id 列表
    """
    DRAW = pygame.event.custom_type()
    """
    抽牌

    数据:
        card: 抽到的卡牌
        player: 抽牌方
    """
    USE = pygame.event.custom_type()
    """
    使用卡牌, 包括单位部署与指令

    数据:
        card: 使用的卡牌
        source: 触发源, 一般为卡牌自身
        player: 使用者
        targets: 使用时的目标列表
    """
    USE_AFTER = pygame.event.custom_type()
    """
    指令使用后, 在指令效果结算完成后触发

    数据:
        card: 使用的卡牌
        source: 触发源
        player: 使用者
        targets: 使用时的目标列表
    """
    PLAY = USE
    """使用卡牌, USE 的别名"""
    TARGETED = pygame.event.custom_type()
    """
    卡牌被效果指向

    数据:
        target: 被指向的卡牌
        source: 指向来源卡牌
        player: 发起方
    """
    FORECAST = pygame.event.custom_type()
    """
    友方进行预报

    数据:
        player: 预报方
        source: 预报来源卡牌
    """
    RETREAT = pygame.event.custom_type()
    """
    单位撤退

    数据:
        card: 撤退的单位
        player: 控制者
        source: 来源卡牌
    """
    MOVE = pygame.event.custom_type()
    """
    单位移动

    数据:
        card: 移动的单位
        player: 操作者
        line: 目标战线
    """
    ATTACK = pygame.event.custom_type()
    """
    单位攻击

    数据:
        card: 攻击单位
        target: 目标单位或总部
        player: 攻击方
    """
    DAMAGED = pygame.event.custom_type()
    """
    受到伤害

    数据:
        target: 受伤对象
        amount: 伤害量
        kind: DamageType
        source: 来源卡牌或 None
    """
    BUFF = pygame.event.custom_type()
    """
    攻击力或防御力增加

    数据:
        target: 被增益对象
        at: 攻击力增量
        df: 防御力增量
    """
    CHOICE_RESOLVED = pygame.event.custom_type()
    """
    三选一结算

    数据:
        card: 被选中的卡牌
        player: 选择方
    """
    LEAVE = pygame.event.custom_type()
    """
    单位离开战场, 被消灭是 way=DESTROYED 的特殊情况

    数据:
        card: 离开的单位
        player: 控制者
        way: LeaveMethod
        source: 来源卡牌或 None
    """
    ENTER = pygame.event.custom_type()
    """
    单位进入场上, 包括部署与效果加入

    数据:
        card: 进入的单位
        player: 控制者
        method: EntryMethod
    """
    ADD_TO_HAND = pygame.event.custom_type()
    """
    将一张卡牌加入手牌

    数据:
        card: 加入的卡牌
        player: 获得方
    """
    ADD_TO_DECK = pygame.event.custom_type()
    """
    将一张卡牌加入卡组

    数据:
        card: 加入的卡牌
        player: 获得方
        index: 在卡组中的位置
    """
    ADD_TO_BOARD = pygame.event.custom_type()
    """
    将一张卡牌加入场上

    数据:
        card: 加入的卡牌
        player: 控制者
    """
    LOOP = pygame.event.custom_type()
    """
    每帧触发的循环事件, 用于光环类效果刷新

    数据:
        player: 当前回合所有者
        dt: 距上一帧的毫秒数
    """
    TURN_START = pygame.event.custom_type()
    """
    回合开始

    数据:
        player: 回合所有者
    """
    TURN_END = pygame.event.custom_type()
    """
    回合结束

    数据:
        player: 刚结束回合的玩家
    """
    COUNTDOWN = pygame.event.custom_type()
    """
    倒计时降低

    数据:
        card: 倒计时所在的卡牌
        player: 控制者
        remaining: 降低后的剩余值
    """
    DISCARD = pygame.event.custom_type()
    """
    卡牌被弃掉

    数据:
        card: 被弃掉的卡牌
        player: 所属玩家
    """
    SHUFFLE = pygame.event.custom_type()
    """
    卡组洗切

    数据:
        player: 卡组所有者
    """
    INTEL_OVERFLOW = pygame.event.custom_type()
    """
    情报溢出

    数据:
        player: 情报使用方
        amount: 溢出数量
    """
    DEVELOP = pygame.event.custom_type()
    """
    开发选取完成

    数据:
        card: 选中的卡牌
        player: 选取方
        source: 开发来源
    """
    LOOT = pygame.event.custom_type()
    """
    战利品选取完成

    数据:
        card: 选中的卡牌
        player: 选取方
        source: 来源
    """


# 战斗开始事件, 会被投递到 pygame 事件队列
BATTLE_START: int = EventType.BATTLE_START


def trigger_id(trigger: "EventType | str | int") -> int:
    """
    把触发器统一转换成 pygame 事件编号

    字符串会先按 EventType 成员名匹配, 再按关键词 id 匹配触发型关键词

    Args:
        trigger: EventType 成员, 事件名, 关键词 id 或事件编号

    Returns:
        事件编号, 无法识别时为 0
    """
    if isinstance(trigger, str):
        member = EventType.__members__.get(trigger)
        if member is not None:
            return int(member)
        keyword = cards.keywords.get(trigger)
        if keyword is not None:
            return keyword.trigger
        for keyword in cards.keywords.values():
            if keyword.name == trigger:
                return keyword.trigger
        return 0
    return int(trigger)


@dataclass
class Keyword:
    """
    卡牌上的关键词实例

    Attributes:
        keyword_id: 关键词标识
        val: 关键词数值; 重甲/情报为 int, 流亡等为 str, 普通关键词为 None
    """
    keyword_id: str = ""
    val: int | str | None = None


COMBAT_KEYWORDS: frozenset[str] = frozenset(
    {"fury", "blitz", "guard", "shock", "ambush", "smoke", "armor"}
)
"""对战词条集合; 重甲是带数值的关键词"""


def has_combat_keyword(card: Card) -> bool:
    """
    判断单位是否具有对战词条

    Args:
        card: 单位

    Returns:
        是否具有奋战/闪击/守护/重甲/冲击/伏击/烟幕
    """
    return card.armor > 0 or any(
        card.has_keyword(keyword) for keyword in COMBAT_KEYWORDS
    )


class Procedure:
    """流程类, 用于响应(TODO)"""
    def __init__(
        self,
        trigger: "EventType | str | int | Keyword",
        condition: Callable[["Card", Event, "BattleGround"], bool],
        action: Callable[["Card", Event, "BattleGround"], None],
        target_valid: Callable[["Card", "Player", "BattleGround"], bool] | None = None,
        any_zone: bool = False,
    ) -> None:
        """
        __init__

        注册流程

        Args:
            trigger: 触发器, 可以是事件类型、事件名、事件编号或关键词
            condition: 条件, 运行时执行判断
            action: 执行器
            target_valid: 指向目标合法性判断, 为 None 表示不需要指向
            any_zone: 是否允许在卡组/手牌中响应; 默认只允许在场上
        """
        self.target_valid: Callable[["Card", "Player", "BattleGround"], bool] | None = target_valid
        """指向目标合法性判断"""
        self.any_zone: bool = any_zone
        """是否允许在卡组/手牌中响应"""
        self.trigger_keyword: str | None = None
        """触发器对应的关键词 id, 直接写事件时为 None"""
        if isinstance(trigger, Keyword):
            # 关键词触发器: 使用关键词定义里的事件与关键词 id
            self.trigger_keyword = trigger.keyword_id
            keyword_data = cards.keywords.get(trigger.keyword_id)
            self.trigger = (
                int(keyword_data.trigger)
                if keyword_data is not None and keyword_data.trigger
                else trigger_id(trigger.keyword_id)
            )
        else:
            self.trigger = trigger_id(trigger)
            if isinstance(trigger, str) and trigger not in EventType.__members__:
                for keyword in cards.keywords.values():
                    if keyword.keyword_id == trigger or keyword.name == trigger:
                        self.trigger_keyword = keyword.keyword_id
                        break
        self.condition: Callable[["Card", Event, "BattleGround"], bool] = condition
        """触发条件"""
        self.action: Callable[["Card", Event, "BattleGround"], None] = action
        """执行器"""

    def __call__(self, card: "Card", event: Event, battleground: "BattleGround") -> None:
        """
        __call__

        调用流程

        Args:
            card (Card): 流程所属卡牌
            event (Event): 事件
            battleground (BattleGround): 战场对象
        """
        self.run(card, event, battleground)

    def run(self, card: "Card", event: Event, ground: "BattleGround") -> None:
        """
        处理事件

        Args:
            card: 流程所属卡牌
            event: 事件
            ground: 战斗全局参数
        """
        if event.type != self.trigger:
            return
        if not self.any_zone:
            # 默认只有场上卡牌响应; 使用指令时卡牌在手中, 死亡时已在弃牌堆
            if event.type == EventType.USE:
                if card.zone not in (Zone.HAND, Zone.BOARD):
                    return
            elif event.type == EventType.LEAVE and event.dict.get("card") is card:
                pass
            elif card.zone is not Zone.BOARD:
                return
        if self.condition(card, event, ground):
            self.action(card, event, ground)


# ==================== 卡牌实体 ====================


def _empty_procedures() -> list[Procedure]:
    """返回空流程列表"""
    return []


@dataclass
class KeywordData(Keyword):
    """
    关键词定义, 来自 keywords/ 目录下的单个文件

    Attributes:
        keyword_id: 关键词标识, 取文件名
        name: 中文显示名
        description: 关键词说明
        icon: 图标文件名, 位于 assets/keyword/
        procedures: 关键词附带的流程列表
        trigger: 关键词对应的触发器, 0 表示不是触发型关键词
        trigger_condition: 触发型关键词的附加条件, 为 None 时不额外判断
        val: 关键词默认数值, 普通关键词为 None
    """
    name: str = ""
    description: str = ""
    icon: str = ""
    procedures: list[Procedure] = field(default_factory=_empty_procedures)
    trigger: int = 0
    trigger_condition: Callable[..., bool] | None = None

    def with_val(self, value: int | str) -> Keyword:
        """
        返回带指定数值的关键词实例

        Args:
            value: 关键词数值

        Returns:
            新的关键词实例
        """
        return Keyword(self.keyword_id, value)


class Card:
    """
    卡牌

    一张卡牌无论处于卡组/手牌/战场/弃牌区/移除区, 都是同一个对象
    类型由 type 字段区分, at/df 等字段只对五种单位类型有意义

    Attributes:
        type: 卡牌类型
        cost: 花费
        name: 卡牌名称
        country: 所属国家
        description: 卡面信息
        keywords: 关键词列表
        effect: 卡牌效果, 效果系统待设计
        at: 攻击力(单位)
        df: 防御力(单位)
        operation_cost: 行动花费(单位)
        display_name: 中文显示名称
        text: 中文卡面描述
        art: 卡图文件名, 位于 assets/cards/{国家}/
        heal_self: 指令是否治疗己方总部而非伤害敌方总部
        controller: 当前控制者
        owner: 所有者
        line: 所在战线, 未部署时为 None
        zone: 所在区域
        deployed_turn: 部署时的回合序号
        acted_turn: 最近一次移动或攻击的回合序号
    """

    def __init__(
        self,
        type: CardType,
        cost: int,
        name: str,
        country: Country,
        description: str = "",
        keywords: list[str] | None = None,
        keyword_values: dict[str, int | str] | None = None,
        effect: Any | None = None,
        at: int = 0,
        df: int = 0,
        operation_cost: int = 0,
        display_name: str = "",
        text: str = "",
        art: str = "",
        heal_self: bool = False,
        procedures: list[Procedure] | None = None,
        tags: list[str] | None = None,
        card_id: str = "",
        sub_type: str = "",
    ) -> None:
        """
        创建卡牌

        Args:
            type: 卡牌类型
            cost: 花费
            name: 卡牌名称, 一般等于文件名
            country: 所属国家
            description: 卡面信息
            keywords: 关键词 id 列表
            keyword_values: 关键词数值
            effect: 指令的传统效果函数
            at: 攻击力
            df: 防御力
            operation_cost: 行动花费
            display_name: 中文显示名称
            text: 中文卡面描述
            art: 卡图文件名, 位于 assets/cards/{国家}/
            heal_self: 指令是否治疗己方总部
            procedures: 流程列表
            tags: 卡牌自带的标签
        """
        self.type: CardType = type
        self.card_id: str = card_id
        self.sub_type: str = sub_type
        self.last_trigger_turn: int = -1
        self._cost: IntAttr = IntAttr(cost, "cost", self)
        self.name: str = name
        self.country: Country = country
        self.description: str = description
        self.keywords: list[str] = keywords if keywords is not None else []
        self.keyword_values: dict[str, int | str] = (
            keyword_values if keyword_values is not None else {}
        )
        self.base_keywords: list[str] = list(self.keywords)
        self.effect: Any | None = effect
        self._at: IntAttr = IntAttr(at, "at", self)
        self._df: IntAttr = IntAttr(df, "df", self)
        self._operation_cost: IntAttr = IntAttr(operation_cost, "operation_cost", self)
        self.display_name: str = display_name
        self.text: str = text
        self.art: str = art
        self.heal_self: bool = heal_self
        self.procedures: list[Procedure] = procedures if procedures is not None else []
        self.controller: Player = Player.A  # 默认控制者, 进入卡组/手牌/场上时由流程重新指定
        self.owner: Player | None = None
        self.line: "Line | None" = None
        self.zone: Zone = Zone.DECK
        self.last_damage_type: DamageType = DamageType.OTHER
        self.deployed_turn: int = -1
        self.acted_turn: int = -1
        self.moved_turn: int = -1
        self.attacked_turn: int = -1
        self.damage_time: int = 0
        self.damage_amount: int = 0
        self.last_damage_taken: int = 0
        self.overflow_damage: int = 0
        self.suppressed: bool = False
        self.suppressed_turn: int = -1
        self.suppressed_until_turn: int = -1
        self.ambush_used_turn: int = -1
        self.attacks_turn: int = 0
        self.aura_at: int = 0
        self.aura_keywords: set[str] = set()
        self.aura_applied: set[int] = set()
        self.aura_sources: set[int] = set()
        self.temp_at: int = 0
        self.tags: set[str] = set(tags) if tags is not None else set()
        self.base_tags: set[str] = set(self.tags)
        self.revealed: bool = False
        self.initial_at: int = at
        self.initial_df: int = df
        self.initial_operation_cost: int = operation_cost
        self.inhibited: bool = False
        self.initial_cost: int = cost
        self.at_bonus: int = 0
        self.df_bonus: int = 0
        self.cost_bonus: int = 0
        self.max_df: int = df
        self.buff_at: int = 0
        self.buff_df: int = 0
        self.buff_time: int = 0

    @property
    def targeted(self) -> bool:
        """指令是否需要在使用前指向目标"""
        return self.type is CardType.ORDER and any(
            procedure.target_valid is not None for procedure in self.procedures
        )

    @property
    def target_valid(self) -> Callable[..., bool] | None:
        """指向目标合法性判断"""
        for procedure in self.procedures:
            if procedure.target_valid is not None:
                return procedure.target_valid
        return None

    @property
    def armor(self) -> int:
        """重甲值, 来自关键词数值"""
        value = self.keyword_values.get("armor")
        return value if isinstance(value, int) else 0

    @property
    def intel(self) -> int:
        """情报值, 来自关键词数值"""
        value = self.keyword_values.get("intel")
        return value if isinstance(value, int) else 0

    @property
    def immune(self) -> bool:
        """是否免疫伤害"""
        return self.has_keyword("immune")

    @property
    def exile_to(self) -> Country | None:
        """流亡目标国家, 来自关键词数值"""
        value = self.keyword_values.get("exile")
        if isinstance(value, Country):
            return value
        if isinstance(value, str):
            try:
                return Country(value)
            except ValueError:
                try:
                    return Country[value.upper()]
                except KeyError:
                    return None
        return None

    @property
    def at(self) -> int:
        """攻击力"""
        return self._at.val

    @at.setter
    def at(self, value: int) -> None:
        self._at.set(value)

    @property
    def df(self) -> int:
        """防御力"""
        return self._df.val

    @df.setter
    def df(self, value: int) -> None:
        # 防御力修改钩子: 511 团等卡牌的防御力不能降到 1 以下
        if self.has_tag(CardTag.DEFENSE_FLOOR_ONE):
            value = max(1, value)
        self._df.set(value)

    @property
    def cost(self) -> int:
        """卡面花费, 用于预报分级"""
        return self._cost.val

    @cost.setter
    def cost(self, value: int) -> None:
        self._cost.set(value)

    @property
    def effective_cost(self) -> int:
        """实际支付花费, 自动使用卡牌为 0"""
        if self.has_keyword("pfwd"):
            return 0
        return self._cost.val

    @property
    def operation_cost(self) -> int:
        """行动花费"""
        return self._operation_cost.val

    @operation_cost.setter
    def operation_cost(self, value: int) -> None:
        self._operation_cost.set(value)

    def buff(self, at: int = 0, df: int = 0) -> None:
        """
        增加攻击力与防御力, 并记录用于绿色提示

        Args:
            at: 攻击力增量
            df: 防御力增量
        """
        self.at += at
        self.df += df
        cap = MAX_HQ_DF if self.is_hq else MAX_STAT
        self.at = min(self.at, cap)
        self.df = min(self.df, cap)
        self.max_df = max(self.max_df, self.df)
        self.buff_at = at
        self.buff_df = df
        self.buff_time = pygame.time.get_ticks()

    def apply_permanent(self, at: int = 0, df: int = 0, cost: int = 0) -> None:
        """
        应用会跨区域保留的永久修改

        Args:
            at: 攻击力增量
            df: 防御力增量
            cost: 花费增量, 负数为减费
        """
        self.at_bonus += at
        self.df_bonus += df
        self.cost_bonus += cost
        self.at = min(MAX_STAT, self.at + at)
        self.df = min(MAX_STAT, self.df + df)
        self.max_df = max(self.max_df, self.df)
        self.cost = max(0, self.initial_cost + self.cost_bonus)

    def reset_state(self, clear_modifiers: bool = False) -> None:
        """
        重置为初始状态

        Args:
            clear_modifiers: 是否清除永久修改, 回手/回卡组时使用
        """
        if self.has_tag(CardTag.IGNORE_RESET):
            return
        # 先移除旧光环, 避免重置后再次扣除 aura_at
        self.clear_auras()
        if clear_modifiers:
            self.at_bonus = 0
            self.df_bonus = 0
            self.cost_bonus = 0
        self.at = min(MAX_STAT, self.initial_at + self.at_bonus)
        self.temp_at = 0
        self.aura_applied.clear()
        self.aura_sources.clear()
        self.df = min(MAX_STAT, self.initial_df + self.df_bonus)
        self.max_df = self.df
        self.operation_cost = self.initial_operation_cost
        self.cost = max(0, self.initial_cost + self.cost_bonus)
        self.damage_amount = 0
        self.buff_at = 0
        self.buff_df = 0
        self.tags = set(self.base_tags)
        self.keywords = list(self.base_keywords)
        self.suppressed = False
        self.suppressed_turn = -1
        self.suppressed_until_turn = -1
        self.ambush_used_turn = -1
        self.attacks_turn = 0
        self.deployed_turn = -1

    def clear_auras(self) -> None:
        """清除光环提供的临时修改"""
        if self.aura_at:
            self.at -= self.aura_at
            self.aura_at = 0
        for keyword in self.aura_keywords:
            if keyword in self.keywords:
                self.keywords.remove(keyword)
        self.aura_keywords.clear()

    def begin_loop_auras(self) -> None:
        """LOOP 开始前清空本帧光环来源记录"""
        self.aura_sources.clear()

    def finish_loop_auras(self) -> None:
        """LOOP 结束后移除已经离场的光环来源记录"""
        self.aura_applied.intersection_update(self.aura_sources)

    @property
    def is_unit(self) -> bool:
        """是否为单位"""
        return self.type.is_unit

    @property
    def is_hq(self) -> bool:
        """是否为总部"""
        return self.type is CardType.HQ

    def has_keyword(self, keyword_id: str) -> bool:
        """是否具有指定关键词"""
        if self.inhibited:
            return False
        return keyword_id in self.keywords or keyword_id in self.aura_keywords

    def keyword_val(self, keyword_id: str) -> int | str | None:
        """
        返回关键词的数值

        Args:
            keyword_id: 关键词 id

        Returns:
            关键词数值, 没有时返回 None
        """
        return self.keyword_values.get(keyword_id)

    def add_temporary_at(self, amount: int) -> None:
        """
        增加本回合内有效的攻击力

        Args:
            amount: 攻击力增量
        """
        if amount <= 0:
            return
        self.temp_at += amount
        self.at += amount

    def clear_temporary(self) -> None:
        """清除本回合内有效的攻击力"""
        if self.temp_at:
            self.at -= self.temp_at
            self.temp_at = 0

    def add_aura(self, at: int = 0, keyword: str | None = None) -> None:
        """
        添加光环提供的临时修改

        Args:
            at: 攻击力增量
            keyword: 临时关键词
        """
        if self.inhibited:
            return
        if at:
            self.aura_at += at
            self.at += at
        if keyword is not None and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.aura_keywords.add(keyword)

    def has_tag(self, tag: str) -> bool:
        """
        判断是否拥有某个标签

        Args:
            tag: 标签

        Returns:
            是否拥有
        """
        return tag in self.tags

    def destroy(self, target: "Card", ground: "BattleGround") -> None:
        """
        以自身为来源消灭目标

        Args:
            target: 目标单位
            ground: 战斗全局参数
        """
        ground.kill(target, source=self)

    def remove(self, target: "Card", ground: "BattleGround") -> None:
        """
        以自身为来源移除目标

        Args:
            target: 目标单位
            ground: 战斗全局参数
        """
        ground.remove_unit(target, source=self)

    def return_hand(self, target: "Card", ground: "BattleGround") -> None:
        """
        以自身为来源将目标返回手牌

        Args:
            target: 目标单位
            ground: 战斗全局参数
        """
        ground.return_unit(target, source=self)

    def add_tag(self, tag: str) -> None:
        """
        添加标签

        Args:
            tag: 标签
        """
        self.tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        """
        移除标签

        Args:
            tag: 标签
        """
        self.tags.discard(tag)

    @property
    def slot_index(self) -> int:
        """战线内位置索引, 未部署时为 -1"""
        if self.line is None:
            return -1
        return self.line.units.index(self)

    def update(self, event: Event, ground: "BattleGround") -> None:
        """
        接收事件并触发自身效果

        Args:
            event: 事件
            ground: 战斗全局参数
        """
        for procedure in self.procedures:
            if event.type == EventType.ENTER and event.dict.get("deferred_card") is self:
                return
            if procedure.trigger != event.type:
                continue
            keyword_id = procedure.trigger_keyword
            if keyword_id is not None:
                if keyword_id not in self.keywords:
                    continue
                keyword = cards.keywords.get(keyword_id)
                if (
                    keyword is not None
                    and keyword.trigger_condition is not None
                    and not keyword.trigger_condition(self, event, ground)
                ):
                    continue
            procedure.run(self, event, ground)

    def take_damage(self, amount: int) -> bool:
        """
        受到伤害, DF 归零则被消灭并离开战场

        Args:
            amount: 伤害量

        Returns:
            是否被消灭
        """
        self.df -= amount
        self.damage_amount = amount
        self.damage_time = pygame.time.get_ticks()
        if self.df <= 0:
            if self.line is not None:
                self.line.remove(self)
            return True
        return False

    def move(self, line: "Line", index: int | None = None) -> bool:
        """
        移动到目标战线, 移动规则待细化

        Args:
            line: 目标战线
            index: 目标战线内位置, 默认追加

        Returns:
            是否移动成功
        """
        # TODO: 移动规则待细化(油费, 移动范围, 前线归属等)
        if line is self.line:
            if index is None or self not in line.units:
                return True
            line.units.remove(self)
            line.units.insert(max(0, min(index, len(line.units))), self)
            return True
        if len(line.units) >= line.capacity:
            return False
        if line.kind is LineKind.FRONT and line.owner is not None and line.owner is not self.controller:
            return False
        if self.line is not None:
            self.line.remove(self)
        return line.add(self, index)

    def attack(self, target: "Card") -> None:
        """
        攻击目标, 攻击规则待细化

        Args:
            target: 目标单位或总部
        """
        # TODO: 攻击规则待细化(反击, 油费, 目标合法性等)
        target.take_damage(self.at)



class Line:
    """
    战线, 最多容纳 5 个卡位

    支援阵线中总部也占一个卡位, 并且和单位一样参与排列

    Attributes:
        kind: 战线种类
        owner: 支援阵线的所属玩家; 前线为当前占据方或 None
        units: 有序单位列表, 保持左右顺序
        hq_index: 总部在卡位顺序中的位置, 0 到 len(units)
    """

    MAX_UNITS: int = 5

    def __init__(self, kind: LineKind, owner: Player | None = None) -> None:
        """
        创建战线

        Args:
            kind: 战线种类
            owner: 所属玩家, 前线可为 None
        """
        self.kind: LineKind = kind
        self.owner: Player | None = owner
        self.units: list[Card] = []
        self.hq_index: int = 0

    def item_count(self) -> int:
        """
        返回战线上的卡位数量, 含支援阵线的总部

        Returns:
            卡位数量
        """
        return len(self.units) + (1 if self.kind is LineKind.SUPPORT else 0)

    def add(self, unit: Card, index: int | None = None) -> bool:
        """
        添加单位到战线

        Args:
            unit: 要添加的单位
            index: 卡位插入位置(含总部), 默认追加到末尾

        Returns:
            是否添加成功
        """
        if len(self.units) >= self.capacity:
            return False
        if self.kind == LineKind.FRONT:
            # 前线同时只能有一方单位
            if self.owner is not None and self.owner != unit.controller:
                return False
        if self.kind is LineKind.SUPPORT:
            count = self.item_count()
            item = count if index is None else max(0, min(index, count))
            if item <= self.hq_index:
                position = item
                self.hq_index += 1
            else:
                position = item - 1
        else:
            position = len(self.units) if index is None else max(0, min(index, len(self.units)))
        self.units.insert(position, unit)
        unit.line = self
        if self.kind == LineKind.FRONT:
            self.owner = unit.controller
        return True

    def remove(self, unit: Card) -> None:
        """
        从战线移除单位

        Args:
            unit: 要移除的单位
        """
        if unit in self.units:
            position = self.units.index(unit)
            if self.kind is LineKind.SUPPORT and position < self.hq_index:
                self.hq_index -= 1
            self.units.remove(unit)
        unit.line = None
        if self.kind == LineKind.FRONT and not self.units:
            self.owner = None

    @property
    def capacity(self) -> int:
        """
        战线可容纳的单位数

        Returns:
            支援阵线预留一格给总部, 因此比前线少一格
        """
        return self.MAX_UNITS - 1 if self.kind is LineKind.SUPPORT else self.MAX_UNITS


class Deck:
    """
    卡组, 39 张自选卡牌 + 1 个总部

    Attributes:
        cards: 卡牌列表, 栈顶为末尾
        hq: 总部
    """

    SIZE: int = 39

    def __init__(self, cards: list[Card], hq: Card) -> None:
        """
        创建卡组

        Args:
            cards: 卡牌列表
            hq: 总部
        """
        self.cards: list[Card] = cards
        self.hq: Card = hq

    def draw(self) -> Card | None:
        """
        从卡组顶抽一张牌, 卡组为空时返回 None

        Returns:
            抽到的卡牌, 或 None
        """
        if not self.cards:
            return None
        return self.cards.pop()


class Hand:
    """手牌, 最多 9 张"""

    MAX_CARDS: int = 9

    def __init__(self) -> None:
        """创建空手牌"""
        self.cards: list[Card] = []

    def add(self, card: Card) -> bool:
        """
        加入手牌

        Args:
            card: 卡牌

        Returns:
            是否加入成功
        """
        if len(self.cards) >= self.MAX_CARDS:
            return False
        self.cards.append(card)
        return True

    def remove(self, card: Card) -> None:
        """
        从手牌移除卡牌(粉碎)

        Args:
            card: 卡牌
        """
        if card in self.cards:
            self.cards.remove(card)


class Kredit:
    """
    指挥点与指挥点槽

    Attributes:
        slots: 指挥点槽数量
        credits: 当前指挥点
    """

    MAX_SLOTS: int = 24
    """指挥点槽上限"""
    NATURAL_MAX: int = 12
    """自然增长能达到的槽数上限"""
    START_SLOTS: int = 12
    """初始槽数"""

    def __init__(self) -> None:
        """创建空的指挥点池"""
        self.slots: int = self.START_SLOTS
        self.credits: int = self.START_SLOTS

    def start_turn(self) -> None:
        """回合开始, 自然增长 1 个槽(最多 24), 然后指挥点回满到槽数"""
        if self.slots < self.NATURAL_MAX:
            self.slots += 1
        self.slots = min(self.slots, self.MAX_SLOTS)
        self.credits = self.slots

    def add_slots(self, amount: int) -> None:
        """
        增加指挥点槽, 不超过上限

        Args:
            amount: 增加数量
        """
        self.slots = min(self.slots + amount, self.MAX_SLOTS)

    def remove_slots(self, amount: int) -> None:
        """
        减少指挥点槽, 不低于 0

        Args:
            amount: 减少数量
        """
        self.slots = max(0, self.slots - amount)
        self.credits = min(self.credits, self.slots)

    def add_credits(self, amount: int) -> None:
        """
        增加指挥点, 不超过槽上限

        Args:
            amount: 增加数量
        """
        self.credits = min(self.credits + amount, self.MAX_SLOTS)

    def can_afford(self, cost: int) -> bool:
        """
        判断指挥点是否足够支付花费

        Args:
            cost: 花费

        Returns:
            是否足够
        """
        return self.credits >= cost

    def spend(self, cost: int) -> None:
        """
        扣除指挥点

        Args:
            cost: 花费
        """
        self.credits -= cost

# ==================== 数据仓库 ====================




def _empty_keywords() -> list[Any]:
    """返回空关键词列表"""
    return []


def _empty_tags() -> list[str]:
    """返回空标签列表"""
    return []


class ModInfo(TypedDict):
    """
    mod 元信息, 对应 info.json
    """
    name: str
    """mod 显示名称"""
    version: str
    """mod 版本"""
    author: str
    """mod 作者"""
    description: str
    """mod 内容简介"""
    dependencies: list[str]
    """依赖的 mod id 列表, 会在这些 mod 之后加载"""


@dataclass
class CardData:
    """
    卡牌静态数据, 用于描述一张卡

    card_id 与 name 由 loader 根据 mod 目录名和文件名自动生成, 无需手写

    Attributes:
        type: 卡牌类型
        country: 所属国家
        exile_to: 流亡目标国家, 构筑时按此国家计算国籍
        armor: 重甲值, 受到的对战伤害减少该值, 最多 3
        intel: 情报值, 使用时随机揭示敌方手牌
        cost: 花费
        card_id: 卡牌唯一标识, 格式 mod:name, 自动生成
        name: 卡牌名称, 自动取文件名
        display_name: 中文显示名称
        text: 中文卡面描述
        art: 卡图文件名, 位于 assets/cards/{国家}/
        heal_self: 指令是否治疗己方总部而非伤害敌方总部
        description: 卡面信息
        rare: 稀有度
        keywords: 关键词列表
        at: 攻击力(单位)
        df: 防御力(单位)
        operation_cost: 行动花费(单位)
        effect: 卡牌效果, 可调用对象或效果数据
        procedures: 流程列表
        tags: 卡牌自带的标签
    """
    type: CardType
    country: Country
    cost: int
    exile_to: Country | None = None
    armor: int = 0
    intel: int = 0
    immune: bool = False
    card_id: str = ""
    name: str = ""
    display_name: str = ""
    text: str = ""
    art: str = ""
    heal_self: bool = False
    description: str = ""
    rare: Rarity | str = Rarity.STANDARD
    keywords: list[Keyword] = field(default_factory=_empty_keywords)
    at: int = 0
    df: int = 0
    operation_cost: int = 0
    effect: Any | None = None
    procedures: list[Procedure] = field(default_factory=_empty_procedures)
    tags: list[str] = field(default_factory=_empty_tags)
    sub_type: str = ""

    def __post_init__(self) -> None:
        """把注册关键词统一为 Keyword 实例, 并提取数值/流亡目标"""
        normalized: list[Keyword] = []
        for keyword in self.keywords:
            if not keyword.keyword_id:
                continue
            if keyword.keyword_id == "armor" and isinstance(keyword.val, int):
                self.armor += keyword.val
            elif keyword.keyword_id == "intel" and isinstance(keyword.val, int):
                self.intel += keyword.val
            elif keyword.keyword_id == "exile" and isinstance(keyword.val, str):
                try:
                    self.exile_to = Country(keyword.val)
                except ValueError:
                    try:
                        self.exile_to = Country[keyword.val.upper()]
                    except KeyError:
                        logger.warning("未知流亡国家: %s", keyword.val)
            normalized.append(keyword)
        self.keywords = normalized


class CardsData:
    """
    卡牌数据管理, 记录所有注册的卡牌数据

    同一张卡(同一 card_id)只保存一份 CardData, 所有实例都由它构造
    """

    def __init__(self) -> None:
        """创建空的数据仓库"""
        self._data: dict[str, CardData] = {}
        self.keyword_names: dict[str, str] = {}
        self.keywords: dict[str, "KeywordData"] = {}
        self.loaded_mods: set[str] = set()
        self.mods: dict[str, ModInfo] = {}
        self.zh: dict[str, dict[str, Any]] = {}
        self.mods_dir: Path | None = None

    def asset(self, mod_id: str, relative: str) -> Path | None:
        """
        解析某个 mod 的资源路径

        Args:
            mod_id: mod 标识
            relative: 相对 assets 目录的路径

        Returns:
            资源路径, mod 未加载或文件不存在时为 None
        """
        if self.mods_dir is None or mod_id not in self.mods:
            return None
        path = self.mods_dir / mod_id / "assets" / relative
        return path if path.is_file() else None

    def add(self, data: CardData) -> None:
        """
        注册卡牌数据

        后加载 mod 中同名的卡牌会替换先加载的卡牌, 旧 id 继续作为别名指向新数据

        Args:
            data: 卡牌数据
        """
        for existing_id, existing in list(self._data.items()):
            if existing.name == data.name:
                self._data[existing_id] = data
        self._data[data.card_id] = data

    def replace(self, target_id: str, data: CardData) -> None:
        """
        用新数据替换指定卡牌 id 的实现

        Args:
            target_id: 被替换的卡牌 id
            data: 新卡牌数据
        """
        self._data[target_id] = data

    def get(self, card_id: str) -> CardData | None:
        """
        获取卡牌数据

        Args:
            card_id: 卡牌唯一标识

        Returns:
            卡牌数据, 不存在时返回 None
        """
        return self._data.get(card_id)

    def create(self, card_id: str) -> Card:
        """
        按 id 创建一张新卡牌实例

        Args:
            card_id: 卡牌唯一标识

        Returns:
            新的卡牌实例
        """
        data = self._data.get(card_id)
        if data is None:
            raise KeyError(f"未注册的卡牌: {card_id}")
        return build_card(data)

    def has(self, card_id: str) -> bool:
        """
        判断卡牌是否已注册

        Args:
            card_id: 卡牌唯一标识

        Returns:
            是否已注册
        """
        return card_id in self._data

    def all_ids(self) -> list[str]:
        """
        返回所有已注册的卡牌 id, 同名替换只保留最新 id

        Returns:
            卡牌 id 列表
        """
        seen: set[int] = set()
        result: list[str] = []
        for data in self._data.values():
            key = id(data)
            if key in seen:
                continue
            seen.add(key)
            result.append(data.card_id)
        return result


# 全局卡牌数据
cards = CardsData()

# 别名, 便于访问
keyword_names = cards.keyword_names
loaded_mods = cards.loaded_mods


def build_card(data: CardData) -> Card:
    """
    根据卡牌数据构造卡牌实例

    Args:
        data: 卡牌数据

    Returns:
        卡牌实例
    """
    procedures = list(data.procedures)
    keyword_objects: list[Keyword] = []
    seen_keywords: set[str] = set()
    for keyword in data.keywords:
        if keyword.keyword_id in seen_keywords:
            continue
        seen_keywords.add(keyword.keyword_id)
        keyword_objects.append(keyword)
    keywords: list[str] = [keyword.keyword_id for keyword in keyword_objects]
    keyword_values: dict[str, int | str] = {}
    for keyword in keyword_objects:
        if keyword.val is not None:
            keyword_values[keyword.keyword_id] = keyword.val
    if "guard" in keywords and "smoke" in keywords:
        logger.warning("关键词冲突: %s 同时拥有守护与烟幕, 保留守护", data.name)
        keywords.remove("smoke")
    for keyword_id in keywords:
        keyword = cards.keywords.get(keyword_id)
        if keyword is None:
            logger.warning("未知关键词: %s (卡牌 %s)", keyword_id, data.name)
            continue
        procedures.extend(keyword.procedures)
    return Card(
        type=data.type,
        cost=data.cost,
        name=data.name,
        country=data.country,
        description=data.description,
        keywords=keywords,
        keyword_values=keyword_values,
        effect=data.effect,
        at=data.at,
        df=data.df,
        operation_cost=data.operation_cost,
        display_name=data.display_name,
        text=data.text,
        art=data.art,
        heal_self=data.heal_self,
        procedures=procedures,
        tags=list(data.tags),
        card_id=data.card_id,
        sub_type=data.sub_type,
    )

# ==================== 战斗核心 ====================


def _empty_card_ids() -> list[str]:
    """返回空卡牌 id 列表"""
    return []


@dataclass
class BattleConfig:
    """
    战斗配置

    Attributes:
        host_kind: 本地玩家类型
        guest_kind: 对手类型
        host_country: 本地主国
        guest_country: 对手主国
        host_ally: 本地盟国
        guest_ally: 对手盟国
        host_deck: 本地卡组卡牌 id 列表
        guest_deck: 对手卡组卡牌 id 列表
    """
    host_kind: PlayerKind = PlayerKind.HUMAN
    guest_kind: PlayerKind = PlayerKind.AI
    host_country: Country = Country.GERMANY
    guest_country: Country = Country.SOVIET
    host_ally: Country | None = None
    guest_ally: Country | None = None
    host_deck: list[str] = field(default_factory=_empty_card_ids)
    guest_deck: list[str] = field(default_factory=_empty_card_ids)


@dataclass
class ChooseOption:
    """抉择选项。"""

    card: Card
    action: Callable[[], None]


@dataclass
class ChooseRequest:
    """等待玩家二选一的抉择请求。"""

    player: Player
    source: Card
    options: list[ChooseOption]
    cost: int = 0
    hand_index: int = -1


@dataclass
class SelectionRequest:
    """
    等待玩家选取手牌的请求

    Attributes:
        player: 发起方
        min_count: 最少选取数量
        max_count: 最多选取数量
        callback: 确认后的回调
        filter: 可选的手牌筛选器
        title: 界面提示文本
    """
    player: Player
    min_count: int
    max_count: int
    callback: Callable[[list[Card]], None]
    filter: Callable[[Card], bool] | None = None
    title: str = ""


@dataclass
class CardChoice:
    """
    等待玩家从若干卡牌中选择一张

    Attributes:
        player: 选取方
        cards: 候选卡牌
        destination: 选中后的去处
        develop: 是否为开发选取
        origin_deck: 候选牌是否来自卡组
        source: 来源卡牌
        title: 界面标题
    """
    player: Player
    cards: list[Card]
    source: Card
    destination: Zone = Zone.HAND
    develop: bool = False
    origin_deck: bool = False
    unselected_bottom: bool = False
    loot_event: bool = False
    title: str = ""
    callback: Callable[[Card, list[Card]], None] | None = None
    next_turn: bool = False
    """选中牌是否延迟到下个友方回合开始时加入手牌"""


@dataclass
class PendingTarget:
    """
    等待玩家选择的指向目标

    Attributes:
        player: 发起方
        source: 指向的来源卡牌
        valid: 判断某个目标是否合法
        callback: 选定目标后的执行器
        cancel: 取消指向时的回调
        finish: 结算完成后的回调
    """
    player: Player
    source: Card
    valid: Callable[[Card], bool]
    callback: Callable[[Card], None]
    cancel: Callable[[], None] | None = None
    finish: Callable[[], None] | None = None


@dataclass
class ShadowTimer:
    """
    影子总部计时器

    Attributes:
        remaining: 剩余回合数
        action: 归零时执行的动作
    """
    remaining: int
    action: Callable[[], None]


DEPLOY_FALLBACK_HOOKS: list[Callable[["BattleGround", Player, Card], None]] = []
"""部署兜底流程钩子, 在部署效果之后、ENTER 之前按注册顺序执行"""


class BattleGround:
    """
    战斗全局参数

    Attributes:
        config: 战斗配置
        turn_count: 当前回合序号, 从 1 开始
        first_player: 先手玩家
        turn_owner: 当前回合所有者
        front_line: 前线
        support_lines: 双方支援阵线
        decks: 双方卡组
        hands: 双方手牌
        hqs: 双方总部
        kredits: 双方指挥点
        pending_turn_draws: 回合开始额外抽牌数
        turns_taken: 双方已进行回合数
        discards: 双方弃牌堆
        fatigue: 双方士气伤害次数
        turn_start_countries: 回合开始时双方场上国家
        notice: 当前界面提示文本
        pending_enter_effects: 延迟结算的进入事件
        pending_returns: 延迟返回手牌的单位与来源
        pending_isolated: 被孤立等待返回的单位与返回回合玩家
        pending_actions: 延迟执行的动作
        hooks: 全局事件钩子
        targets: 当前正在结算的卡牌目标列表
        pending_target: 等待玩家选择的指向目标
        pending_selection: 等待玩家确认的手牌选取
        pending_choice: 等待玩家确认的三选一
        last_choice_result: 最近一次三选一结果
        act_rule: 行动判定钩子, 返回 None 时使用默认标签规则
        winner: 已分出胜负时的胜方
    """

    def __init__(self, config: BattleConfig, deck_a: Deck, deck_b: Deck) -> None:
        """
        创建战斗

        Args:
            config: 战斗配置
            deck_a: 玩家 A 的卡组
            deck_b: 玩家 B 的卡组
        """
        self.config: BattleConfig = config
        """战斗配置"""
        self.turn_count: int = 1
        """当前回合序号, 从 1 开始"""
        self.first_player: Player = random.choice((Player.A, Player.B))
        """先手玩家"""
        self.turn_owner: Player = Player.A
        """当前回合所有者"""
        self.front_line: Line = Line(LineKind.FRONT)
        """前线"""
        self.support_lines: dict[Player, Line] = {
            Player.A: Line(LineKind.SUPPORT, Player.A),
            Player.B: Line(LineKind.SUPPORT, Player.B),
        }
        """双方支援阵线"""
        self.decks: dict[Player, Deck] = {Player.A: deck_a, Player.B: deck_b}
        """双方卡组"""
        self.hands: dict[Player, Hand] = {Player.A: Hand(), Player.B: Hand()}
        """双方手牌"""
        self.hqs: dict[Player, Card] = {Player.A: deck_a.hq, Player.B: deck_b.hq}
        """双方总部"""
        self.kredits: dict[Player, Kredit] = {Player.A: Kredit(), Player.B: Kredit()}
        """双方指挥点"""
        self.pending_turn_draws: dict[Player, int] = {Player.A: 0, Player.B: 0}
        """回合开始额外抽牌数"""
        self.turns_taken: dict[Player, int] = {Player.A: 0, Player.B: 0}
        """双方已进行回合数"""
        self.discards: dict[Player, list[Card]] = {Player.A: [], Player.B: []}
        """双方弃牌堆"""
        self.fatigue: dict[Player, int] = {Player.A: 0, Player.B: 0}
        """双方士气伤害次数"""
        self.turn_start_countries: dict[Player, set[Country]] = {Player.A: set(), Player.B: set()}
        """回合开始时双方场上国家, 用于协力"""
        self.notice: str = ""
        """当前界面提示文本"""
        self.pending_enter_effects: list[tuple[int, Card, Event]] = []
        """延迟结算的进入事件"""
        self.pending_returns: list[tuple[int, Card, Card]] = []
        """延迟返回手牌的单位与来源"""
        self.pending_isolated: list[tuple[Card, Player]] = []
        """被孤立等待返回的单位与返回回合玩家"""
        self.shadow_hqs: dict[Player, Card | None] = {Player.A: None, Player.B: None}
        """双方影子总部, 不进入战线也不参与一般计算"""
        self.shadow_timers: dict[Player, list[ShadowTimer]] = {
            Player.A: [],
            Player.B: [],
        }
        """影子总部计时器"""
        self.weather_used_turn: dict[Player, int] = {Player.A: -1, Player.B: -1}
        """双方最近一次使用天气的回合序号"""
        self.current_weather: dict[Player, str | None] = {
            Player.A: None,
            Player.B: None,
        }
        """双方当前天气"""
        self.pending_actions: list[tuple[int, Callable[[], None]]] = []
        """延迟执行的动作"""
        self.hooks: dict[int, list[Callable[[Event, "BattleGround"], None]]] = {}
        """全局事件钩子"""
        self.targets: list[Card] = []
        """当前正在结算的卡牌目标列表"""
        self.pending_target: PendingTarget | None = None
        """等待玩家选择的指向目标"""
        self.pending_selection: SelectionRequest | None = None
        """等待玩家确认的手牌选取"""
        self.pending_choice: CardChoice | None = None
        """等待玩家确认的三选一"""
        self.pending_choose: ChooseRequest | None = None
        """等待玩家确认的抉择"""
        self.last_choice_result: tuple[Card, list[Card]] | None = None
        """最近一次三选一结果"""
        self.act_rule: Callable[[Card, str], bool | None] | None = None
        """行动判定钩子, 返回 None 时使用默认标签规则"""
        self.winner: Player | None = None
        """已分出胜负时的胜方"""
        self.last_destroyed_ground: dict[Player, Card | None] = {
            Player.A: None,
            Player.B: None,
        }
        """每方最后被消灭的陆军单位"""
        deck_a.hq.line = self.support_lines[Player.A]
        deck_b.hq.line = self.support_lines[Player.B]

    def kind_of(self, player: Player) -> PlayerKind:
        """
        返回玩家的类型

        Args:
            player: 玩家

        Returns:
            玩家类型
        """
        return self.config.host_kind if player is Player.A else self.config.guest_kind

    def country_of(self, player: Player) -> Country:
        """
        返回玩家的主国

        Args:
            player: 玩家

        Returns:
            主国
        """
        return self.config.host_country if player is Player.A else self.config.guest_country

    def start(self) -> None:
        """开始战斗, 洗牌发牌, 初始化先手指挥点并发出 BATTLE_START 事件"""
        random.shuffle(self.decks[Player.A].cards)
        random.shuffle(self.decks[Player.B].cards)
        self.deal_initial_hands()
        self.kredits[self.first_player].credits = self.kredits[self.first_player].slots
        self.turns_taken[self.first_player] = 1
        start_event = pygame.event.Event(
            BATTLE_START,
            host=self.config.host_kind,
            guest=self.config.guest_kind,
            host_country=self.config.host_country,
            guest_country=self.config.guest_country,
            host_ally=self.config.host_ally,
            guest_ally=self.config.guest_ally,
            main_a=self.config.host_country,
            ally_a=self.config.host_ally,
            main_b=self.config.guest_country,
            ally_b=self.config.guest_ally,
            host_deck=self.config.host_deck,
            guest_deck=self.config.guest_deck,
        )
        pygame.event.post(start_event)
        self.emit(start_event)
        self.emit(Event(EventType.TURN_START, player=self.first_player))
        if self.config.host_kind is PlayerKind.HUMAN:
            self.start_mulligan(Player.A)

    def deal_initial_hands(self) -> None:
        """对局开始发牌, 先手 4 张后手 5 张"""
        second = self.first_player.opponent
        for _ in range(4):
            self.draw(self.first_player, self.special_source(self.first_player))
        for _ in range(5):
            self.draw(second, self.special_source(second))

    def special_source(self, player: Player) -> Card:
        """
        返回回合开始抽牌等系统行为的特殊来源

        Args:
            player: 玩家

        Returns:
            带有 SPECIAL_SOURCE 标签的友方总部
        """
        hq = self.hqs[player]
        hq.add_tag(CardTag.SPECIAL_SOURCE)
        return hq

    def draw(self, player: Player, source: Card) -> Card | None:
        """
        为玩家抽一张牌, 手牌满 9 张时弃掉抽到的牌

        卡组为空时改为对总部造成士气伤害, 第 X 次受到 X 点

        Args:
            player: 玩家
            source: 抽牌来源, 回合开始时为带 SPECIAL_SOURCE 标签的总部

        Returns:
            抽到的卡牌, 卡组为空时为 None
        """
        card = self.decks[player].draw()
        if card is None:
            self.morale_damage(player, source=source)
            return None
        if self.hands[player].add(card):
            card.zone = Zone.HAND
            self.auto_use_card(card, player)
        else:
            self.discard_card(player, card)
        self.emit(Event(EventType.DRAW, card=card, player=player, source=source))
        return card

    def apply_intel(self, player: Player, card: Card) -> None:
        """
        结算情报: 随机揭示敌方手牌, 并计算溢出情报

        Args:
            player: 使用方
            card: 使用的卡牌
        """
        if card.intel <= 0:
            return
        enemy_hand = self.hands[player.opponent].cards
        hidden = [item for item in enemy_hand if not item.revealed]
        hidden_count = len(hidden)
        random.shuffle(hidden)
        for item in hidden[: card.intel]:
            item.revealed = True
        overflow = max(0, card.intel - hidden_count)
        if overflow > 0:
            self.emit(
                Event(
                    EventType.INTEL_OVERFLOW,
                    player=player,
                    amount=overflow,
                )
            )

    def morale_damage(
        self,
        player: Player,
        source: Card,
        notify: bool = False,
    ) -> int:
        """
        对玩家总部造成一次士气伤害, 第 X 次受到 X 点

        Args:
            player: 玩家
            notify: 是否显示士气伤害提示
            source: 来源

        Returns:
            本次士气伤害数值
        """
        self.fatigue[player] += 1
        amount = self.fatigue[player]
        logger.debug("士气伤害: 玩家 %s 第 %s 次, %s 点", player, amount, amount)
        self.damage(
            self.hqs[player],
            amount,
            source,
            DamageType.MORALE,
        )
        if notify:
            label = "友方" if player is Player.A else "敌方"
            self.notice = f"{label}总部受到了 {amount} 点士气伤害"
        return amount

    def friendly_countries(self, player: Player) -> set[Country]:
        """
        返回玩家场上单位的国家集合

        Args:
            player: 玩家

        Returns:
            国家集合
        """
        result: set[Country] = set()
        for line in (self.support_lines[player], self.front_line):
            for unit in line.units:
                if unit.controller is player:
                    result.add(unit.country)
        return result

    def check_bond(self, player: Player, card: Card) -> None:
        """
        检查协力: 本回合开始时场上没有同国家友方单位则受到士气伤害

        Args:
            player: 使用方
            card: 使用的卡牌
        """
        if not card.has_keyword("bond"):
            return
        if card.country in self.turn_start_countries[player]:
            return
        self.morale_damage(player, notify=True, source=card)

    def all_targets(self) -> list[Card]:
        """
        返回场上的全部单位与双方总部

        Returns:
            可作为目标的列表
        """
        targets: list[Card] = []
        for line in (self.support_lines[Player.A], self.support_lines[Player.B], self.front_line):
            targets.extend(line.units)
        targets.append(self.hqs[Player.A])
        targets.append(self.hqs[Player.B])
        return targets

    def is_immune(self, target: Card) -> bool:
        """
        判断目标是否具有免疫

        单位自身免疫直接生效; 总部免疫由敌方回合中的友方光环单位提供

        Args:
            target: 单位或总部

        Returns:
            是否免疫伤害
        """
        if not target.is_hq:
            return target.immune
        if target.immune:
            return True
        owner = Player.A if target is self.hqs[Player.A] else Player.B
        if self.turn_owner is owner:
            return False
        for line in (self.support_lines[owner], self.front_line):
            for unit in line.units:
                if unit.controller is owner and unit.has_tag(CardTag.HQ_IMMUNE_ENEMY_TURN):
                    return True
        return False

    def damage(
        self,
        target: Card | list[Card],
        amount: int,
        source: Card,
        kind: DamageType = DamageType.NONE,
    ) -> None:
        """
        对单位或总部造成伤害, 单位死亡时自动送入弃牌堆并广播事件

        Args:
            target: 受伤对象, 可以是单个目标或目标列表
            amount: 伤害量
            kind: 伤害类型
            source: 伤害来源
        """
        targets = target if isinstance(target, list) else [target]
        for item in list(targets):
            # 指令造成的伤害以使用者 HQ 作为来源
            event_source = (
                self.hqs[source.controller]
                if source.type is CardType.ORDER
                else source
            )
            if self.is_immune(item) and kind is not DamageType.MORALE:
                continue
            actual = amount
            if item.is_unit and kind.is_confrontation:
                armor = min(max(item.armor, 0), 3)
                actual = max(0, actual - armor)
                if item.has_tag(CardTag.DAMAGE_CAP_ONE):
                    actual = min(actual, 1)
            if actual <= 0:
                continue
            actual = min(actual, MAX_STAT)
            item.last_damage_type = kind
            item.last_damage_taken = actual
            df_before = item.df if item.is_unit else 0
            item.take_damage(actual)
            if item.is_unit:
                item.overflow_damage = max(0, actual - df_before) if item.df <= 0 else 0
            self.emit(Event(EventType.DAMAGED, target=item, amount=actual, kind=kind, source=event_source))
            if item.is_unit and item.line is None and item.zone is Zone.BOARD:
                self.kill(item, source=event_source)
        self.check_victory()

    def buff(self, target: Card, at: int = 0, df: int = 0) -> None:
        """
        增加攻击力或防御力

        Args:
            target: 单位或总部
            at: 攻击力增量
            df: 防御力增量
        """
        if target.is_hq:
            target.buff(df=df)
        else:
            target.buff(at, df)
        self.emit(Event(EventType.BUFF, target=target, at=at, df=df))

    def add_aura(
        self,
        target: Card,
        source: Card,
        at: int = 0,
        keyword: str | None = None,
    ) -> None:
        """
        应用光环, 并在本次光环首次生效时广播 BUFF

        Args:
            target: 被光环影响的单位
            at: 攻击力增量
            keyword: 临时关键词
            source: 光环来源卡牌
        """
        if target.inhibited or source.inhibited:
            return
        target.add_aura(at=at, keyword=keyword)
        if keyword == "blitz":
            # 光环获得闪击时, 同时清除部署当回合不能行动的限制
            target.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
        source_id = id(source)
        target.aura_sources.add(source_id)
        if source_id not in target.aura_applied:
            target.aura_applied.add(source_id)
            self.emit(
                Event(EventType.BUFF, target=target, at=at, df=0, source=source)
            )

    def kill(self, card: Card, source: Card) -> None:
        """
        把单位送入弃牌堆, 卡牌对象本身不变

        Args:
            card: 被消灭的单位
            source: 伤害来源
        """
        if source.type is CardType.ORDER:
            source = self.hqs[source.controller]
        if card.line is not None:
            card.line.remove(card)
        player = card.controller
        if card.is_unit and card.type in (
            CardType.INFANTRY,
            CardType.ARTILLERY,
            CardType.TANK,
        ):
            self.last_destroyed_ground[player] = card
        if card not in self.discards[player]:
            self.discards[player].append(card)
        card.zone = Zone.DISCARD
        leave_event = Event(
            EventType.LEAVE,
            card=card,
            player=player,
            way=LeaveMethod.DESTROYED,
            source=source,
        )
        card.update(leave_event, self)
        self.emit(leave_event)

    def draw_from_deck(self, player: Player, card: Card, source: Card) -> bool:
        """
        从卡组中抽出指定卡牌

        Args:
            player: 抽牌方
            card: 要抽出的卡牌
            source: 抽牌来源

        Returns:
            是否成功抽到
        """
        deck = self.decks[player].cards
        if card not in deck:
            return False
        deck.remove(card)
        if self.hands[player].add(card):
            card.zone = Zone.HAND
            card.revealed = False
            self.emit(Event(EventType.DRAW, card=card, player=player, source=source))
            return True
        self.discard_card(player, card)
        return False

    def draw_filtered(
        self,
        player: Player,
        predicate: Callable[[Card], bool],
        count: int,
        source: Card,
        random_pick: bool = True,
    ) -> list[Card]:
        """
        按条件从卡组中抽牌

        Args:
            player: 抽牌方
            predicate: 筛选条件
            count: 抽取数量
            source: 抽牌来源
            random_pick: 是否随机选择, 否则取满足条件的最低费

        Returns:
            抽到的卡牌
        """
        drawn: list[Card] = []
        for _ in range(count):
            candidates = [
                item for item in self.decks[player].cards if predicate(item)
            ]
            if not candidates:
                break
            if random_pick:
                card = random.choice(candidates)
            else:
                card = min(candidates, key=lambda item: (item.cost, item.name))
            if not self.draw_from_deck(player, card, source):
                break
            drawn.append(card)
        return drawn

    def add_hook(self, trigger: "EventType | str | int", handler: Callable[[Event, "BattleGround"], None]) -> None:
        """
        注册全局钩子, 在事件广播前调用

        Args:
            trigger: 事件类型, 可用 EventType 成员/事件名/事件编号
            handler: 处理函数
        """
        self.hooks.setdefault(trigger_id(trigger), []).append(handler)

    def emit(self, event: Event, extra_cards: list[Card] | None = None) -> None:
        """
        先执行全局钩子, 再向场上所有单位广播事件

        Args:
            event: 事件
            extra_cards: 不在手牌/卡组/场上但仍需接收事件的卡牌
        """
        for handler in self.hooks.get(event.type, []):
            handler(event, self)
        seen: set[int] = set()
        for line in (self.support_lines[Player.A], self.support_lines[Player.B], self.front_line):
            for unit in list(line.units):
                seen.add(id(unit))
                unit.update(event, self)
        # 手牌与卡组也会收到事件; 默认由 Procedure 的场上条件过滤
        for player in (Player.A, Player.B):
            for card in list(self.hands[player].cards) + list(self.decks[player].cards):
                if id(card) in seen:
                    continue
                seen.add(id(card))
                card.update(event, self)
        for card in extra_cards or []:
            if id(card) in seen:
                continue
            seen.add(id(card))
            card.update(event, self)

    def update(self, dt: int) -> None:
        """
        每帧更新, 广播 LOOP 事件供光环类效果刷新, 并处理延迟结算

        Args:
            dt: 距上一帧的毫秒数
        """
        if self.winner is not None:
            return
        now = pygame.time.get_ticks()
        remaining_enters: list[tuple[int, Card, Event]] = []
        for due, card, event in self.pending_enter_effects:
            if now < due:
                remaining_enters.append((due, card, event))
                continue
            if card.zone is Zone.BOARD and card.line is not None:
                card.update(event, self)
        self.pending_enter_effects = remaining_enters
        remaining_returns: list[tuple[int, Card, Card]] = []
        for due, card, source in self.pending_returns:
            if now < due:
                remaining_returns.append((due, card, source))
                continue
            if card.zone is Zone.BOARD and card.line is not None:
                self.return_unit(card, source)
        self.pending_returns = remaining_returns
        remaining_actions: list[tuple[int, Callable[[], None]]] = []
        for due, action in self.pending_actions:
            if now < due:
                remaining_actions.append((due, action))
                continue
            action()
        self.pending_actions = remaining_actions
        for line in (self.support_lines[Player.A], self.support_lines[Player.B], self.front_line):
            for unit in line.units:
                unit.begin_loop_auras()
                unit.clear_auras()
        self.emit(Event(EventType.LOOP, player=self.turn_owner, dt=dt))
        for line in (self.support_lines[Player.A], self.support_lines[Player.B], self.front_line):
            for unit in line.units:
                unit.finish_loop_auras()

    def begin_turn(self) -> None:
        """回合开始, 清除进入当回合的行动限制, 发出 TURN_START, 回满指挥点并抽一张牌"""
        player = self.turn_owner
        logger.debug("回合开始: 玩家 %s, 回合 %s, 指挥点槽 %s", player, self.turn_count, self.kredits[player].slots)
        self.turn_start_countries[player] = self.friendly_countries(player)
        for line in (self.support_lines[player], self.front_line):
            for unit in line.units:
                if unit.controller is player:
                    unit.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
                    unit.remove_tag(CardTag.MOVED)
                    unit.remove_tag(CardTag.ATTACKED)
                    unit.attacks_turn = 0
        remaining_isolated: list[tuple[Card, Player]] = []
        for card, caster in self.pending_isolated:
            if caster is not player:
                remaining_isolated.append((card, caster))
                continue
            owner = card.controller
            if self.add_unit(owner, card):
                card.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
            else:
                self.move_to_hand(card, owner)
        self.pending_isolated = remaining_isolated
        self.emit(Event(EventType.TURN_START, player=player))
        if self.turns_taken[player] == 0:
            self.kredits[player].credits = self.kredits[player].slots
        else:
            self.kredits[player].start_turn()
        self.turns_taken[player] += 1
        active_timers: list[ShadowTimer] = []
        for timer in self.shadow_timers[player]:
            timer.remaining -= 1
            if timer.remaining > 0:
                active_timers.append(timer)
                continue
            timer.action()
        self.shadow_timers[player] = active_timers
        special_source = self.special_source(player)
        self.draw(player, special_source)
        extra = self.pending_turn_draws[player]
        if extra > 0:
            self.pending_turn_draws[player] = 0
            for _ in range(extra):
                self.draw(player, special_source)

    def end_turn(self) -> None:
        """结束当前回合, 移交回合权并开始对方回合并检查胜负"""
        logger.debug("回合结束: 玩家 %s, 回合 %s", self.turn_owner, self.turn_count)
        player = self.turn_owner
        for line in (
            self.support_lines[Player.A],
            self.support_lines[Player.B],
            self.front_line,
        ):
            for unit in line.units:
                if (
                    unit.suppressed
                    and unit.suppressed_until_turn >= 0
                    and self.turn_count >= unit.suppressed_until_turn
                ):
                    unit.suppressed = False
                    unit.suppressed_until_turn = -1
                elif (
                    unit.controller is player
                    and unit.suppressed
                    and self.turns_taken[player] >= unit.suppressed_turn + 1
                ):
                    unit.suppressed = False
        self.emit(Event(EventType.TURN_END, player=player))
        for line in (
            self.support_lines[Player.A],
            self.support_lines[Player.B],
            self.front_line,
        ):
            for unit in line.units:
                unit.clear_temporary()
        self.turn_owner = self.turn_owner.opponent
        self.turn_count += 1
        self.begin_turn()
        self.check_victory()

    def can_move_now(self, card: Card) -> bool:
        """
        判断单位本回合能否移动

        坦克每回合可分别移动与攻击各一次, 其他单位两者共用一次
        行动限制由标签控制, 回合开始时清除
        可以通过 act_rule 钩子覆盖判定

        Args:
            card: 单位

        Returns:
            能否移动
        """
        if card.suppressed:
            return False
        if self.act_rule is not None:
            override = self.act_rule(card, "move")
            if override is not None:
                return override
        if card.has_tag(CardTag.CANNOT_ACT_WHEN_ENTER) or card.has_tag(CardTag.CANNOT_MOVE):
            return False
        if card.type is CardType.TANK:
            return not card.has_tag(CardTag.MOVED)
        return not card.has_tag(CardTag.MOVED) and not card.has_tag(CardTag.ATTACKED)

    def can_attack_now(self, card: Card) -> bool:
        """
        判断单位本回合能否攻击

        行动限制由标签控制, 坦克可以移动后继续攻击
        可以通过 act_rule 钩子覆盖判定

        Args:
            card: 单位

        Returns:
            能否攻击
        """
        if card.suppressed:
            return False
        if self.act_rule is not None:
            override = self.act_rule(card, "attack")
            if override is not None:
                return override
        if card.has_tag(CardTag.CANNOT_ACT_WHEN_ENTER) or card.has_tag(CardTag.CANNOT_ATTACK):
            return False
        if card.has_keyword("fury"):
            if card.has_tag(CardTag.MOVED):
                return False
            return card.attacks_turn < 2
        if card.type is CardType.TANK:
            return not card.has_tag(CardTag.ATTACKED)
        return not card.has_tag(CardTag.MOVED) and not card.has_tag(CardTag.ATTACKED)

    def can_act(self, card: Card) -> bool:
        """
        判断单位本回合是否还有行动

        Args:
            card: 单位

        Returns:
            能否移动或攻击
        """
        return self.can_move_now(card) or self.can_attack_now(card)

    def is_guarded(self, target: Card) -> bool:
        """
        判断目标是否被相邻的守护单位保护

        Args:
            target: 单位或总部

        Returns:
            是否被守护
        """
        if target.is_hq:
            owner = target.controller
            line = self.support_lines[owner]
            for index, unit in enumerate(line.units):
                unit_position = index if index < line.hq_index else index + 1
                if abs(unit_position - line.hq_index) == 1 and unit.has_keyword("guard"):
                    return True
            return False
        if target.has_keyword("guard"):
            return False
        line = target.line
        if line is None:
            return False
        if target not in line.units:
            return False

        def physical_position(index: int) -> int:
            # 支援阵线中 HQ 占一个物理位置, 不能跨过 HQ 判定相邻
            if line.kind is LineKind.SUPPORT and index >= line.hq_index:
                return index + 1
            return index

        target_index = line.units.index(target)
        target_position = physical_position(target_index)
        for index, unit in enumerate(line.units):
            if unit is target or not unit.has_keyword("guard"):
                continue
            if abs(physical_position(index) - target_position) == 1:
                return True
        return False

    def can_attack(self, player: Player, card: Card, target: Card) -> bool:
        """
        判断单位能否攻击目标

        步兵与坦克只能攻击相邻战线: 支援阵线打前线, 前线打敌方支援阵线与总部
        战斗机、轰炸机、炮兵射程为 2, 可在友方支援阵线直接攻击敌方支援阵线
        轰炸机攻击的阵线若有战斗机, 必须优先攻击战斗机

        Args:
            player: 攻击方
            card: 攻击单位
            target: 目标单位或总部

        Returns:
            是否合法
        """
        if card.controller is not player or card.line is None:
            return False
        if not self.can_attack_now(card):
            return False
        if target.is_hq:
            if target is not self.hqs[player.opponent]:
                return False
            if self.is_guarded(target) and card.type not in (CardType.BOMBER, CardType.ARTILLERY):
                return False
            if card.type in (CardType.INFANTRY, CardType.TANK):
                return card.line.kind is LineKind.FRONT
            if card.type is CardType.BOMBER and self.line_has_fighter(
                self.support_lines[player.opponent], player
            ):
                return False
            return True
        if target.controller is not player.opponent:
            return False
        if self.is_guarded(target) and card.type not in (CardType.BOMBER, CardType.ARTILLERY):
            return False
        if target.has_keyword("smoke") and not target.has_keyword("guard"):
            return False
        if target.has_tag(CardTag.CANNOT_BE_ATTACKED):
            return False
        if card.type in (CardType.INFANTRY, CardType.TANK):
            if card.line.kind is LineKind.SUPPORT:
                return target.line is self.front_line
            return target.line is self.support_lines[player.opponent]
        if card.type is CardType.BOMBER and target.line is not None:
            if self.line_has_fighter(target.line, player) and target.type is not CardType.FIGHTER:
                return False
        return True

    def line_has_fighter(self, line: Line, player: Player) -> bool:
        """
        判断某条战线上是否有敌方的战斗机

        Args:
            line: 战线
            player: 己方

        Returns:
            是否有敌方战斗机
        """
        return any(
            unit.type is CardType.FIGHTER and unit.controller is player.opponent
            for unit in line.units
        )

    def is_large_slam(self, card: Card) -> bool:
        """
        判断单位是否为大拍桌

        Args:
            card: 单位

        Returns:
            是否为大拍桌
        """
        total = card.at + card.df
        level = 2 if total >= 12 else 1 if total >= 10 else 0
        if card.has_tag(CardTag.SLAM_UP_1):
            level += 1
        if card.has_tag(CardTag.SLAM_UP_2):
            level += 2
        return level >= 2

    def action_block_reason(self, card: Card, action: str) -> str:
        """
        返回单位无法移动/攻击的原因。

        Args:
            card: 单位
            action: "move" 或 "attack"

        Returns:
            提示文本; 可以行动时为空字符串
        """
        if card.suppressed:
            return "该单位已被压制，无法行动"
        if action == "move":
            if self.can_move_now(card):
                return ""
            if card.has_tag(CardTag.CANNOT_ACT_WHEN_ENTER):
                return "无法在进入战场的同一回合行动"
            if card.has_tag(CardTag.CANNOT_MOVE):
                return "该单位无法移动"
            if card.has_tag(CardTag.MOVED):
                return "本单位本回合中已经移动过"
            if card.has_tag(CardTag.ATTACKED):
                return "本单位本回合中已经行动过"
            return "该单位当前无法移动"
        if self.can_attack_now(card):
            return ""
        if card.has_tag(CardTag.CANNOT_ACT_WHEN_ENTER):
            return "无法在进入战场的同一回合行动"
        if card.has_tag(CardTag.CANNOT_ATTACK):
            return "该单位无法攻击"
        if card.has_tag(CardTag.ATTACKED):
            return "本单位本回合中已经攻击过"
        if card.has_tag(CardTag.MOVED):
            return "本单位本回合中已经行动过"
        return "该单位当前无法攻击"

    def use_block_reason(self, player: Player, card: Card) -> str:
        """
        返回卡牌无法使用的原因。

        Args:
            player: 使用者
            card: 卡牌

        Returns:
            提示文本; 可以使用时为空字符串
        """
        if player is not self.turn_owner:
            return "现在不是你的回合"
        if self.pending_selection is not None or self.pending_choice is not None or self.pending_choose is not None:
            return "请先完成当前操作"
        if card not in self.hands[player].cards:
            return "该卡不在你的手中"
        if card.sub_type == "weather" and self.weather_used_turn[player] == self.turn_count:
            return "本回合已经使用过天气"
        cost = card.effective_cost
        if not self.kredits[player].can_afford(cost):
            return f"剩余指挥点不足（需要 {cost} 点，当前 {self.kredits[player].credits} 点）"
        if card.is_unit and len(self.support_lines[player].units) >= self.support_lines[player].capacity:
            return "支援阵线已满，无法继续部署单位"
        if not card.is_unit and card.type is not CardType.ORDER:
            return "该卡当前无法使用"
        return ""

    def use_card(self, player: Player, card: Card, index: int | None = None) -> bool:
        """
        使用手牌中的卡牌

        Args:
            player: 使用者
            card: 卡牌
            index: 单位部署的战线内位置

        Returns:
            是否使用成功
        """
        if player is not self.turn_owner:
            return False
        if self.pending_selection is not None:
            return False
        if self.pending_choice is not None:
            return False
        if self.pending_choose is not None:
            return False
        if card not in self.hands[player].cards:
            return False
        if card.sub_type == "weather" and self.weather_used_turn[player] == self.turn_count:
            return False
        effective_cost = card.effective_cost
        if not self.kredits[player].can_afford(effective_cost):
            return False
        if card.is_unit:
            if len(self.support_lines[player].units) >= self.support_lines[player].capacity:
                return False
            targeted_deploy = card.target_valid is not None
            if not targeted_deploy:
                self.kredits[player].spend(effective_cost)
            card.owner = player
            card.controller = player
            operation_cost = card.operation_cost
            card.reset_state()
            card.operation_cost = operation_cost
            card.revealed = False
            card.deployed_turn = self.turn_count
            self.hands[player].remove(card)
            self.support_lines[player].add(card, index)
            card.zone = Zone.BOARD
            card.add_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
            use_event = Event(
                EventType.USE,
                card=card,
                source=card,
                player=player,
                targets=[],
                method=EntryMethod.DEPLOY,
            )
            self.emit(use_event)
            deferred = card.has_tag(CardTag.SLAM_UP_2)
            enter_event = Event(
                EventType.ENTER,
                card=card,
                player=player,
                method=EntryMethod.DEPLOY,
                deferred_card=card if deferred else None,
            )

            paid = not targeted_deploy

            def pay_deploy() -> None:
                nonlocal paid
                if paid:
                    return
                paid = True
                self.kredits[player].spend(effective_cost)

            def finish_deploy() -> None:
                pay_deploy()
                for hook in DEPLOY_FALLBACK_HOOKS:
                    hook(self, player, card)
                if card.zone is not Zone.BOARD:
                    return
                self.emit(enter_event)
                if deferred:
                    effect_event = Event(
                        EventType.ENTER,
                        card=card,
                        player=player,
                        method=EntryMethod.DEPLOY,
                    )
                    self.pending_enter_effects.append(
                        (pygame.time.get_ticks() + 800, card, effect_event)
                    )

            self.apply_intel(player, card)
            if self.pending_target is not None:
                # 部署效果先结算, 结算完成后再广播 ENTER
                self.pending_target.cancel = lambda: self.cancel_deploy(
                    player,
                    card,
                    effective_cost,
                    refund=not targeted_deploy,
                )
                self.pending_target.finish = finish_deploy
            else:
                finish_deploy()
            return True
        if card.type is CardType.ORDER:
            if card.has_tag(CardTag.CHOOSE):
                hand_index = self.hands[player].cards.index(card)
                if card in self.hands[player].cards:
                    self.hands[player].remove(card)
                self.targets = self.all_targets()
                self.emit(
                    Event(
                        EventType.USE,
                        card=card,
                        source=card,
                        player=player,
                        targets=list(self.targets),
                    ),
                    extra_cards=[card],
                )
                if self.pending_choose is not None:
                    self.pending_choose.hand_index = hand_index
                return True
            self.kredits[player].spend(effective_cost)
            if card.sub_type == "weather":
                self.weather_used_turn[player] = self.turn_count
            self.check_bond(player, card)
            self.apply_intel(player, card)
            self.targets = self.all_targets()
            use_event = Event(
                EventType.USE,
                card=card,
                source=card,
                player=player,
                targets=list(self.targets),
            )
            # 指令先离开手牌再结算, 抽牌时手牌已腾出位置
            if card in self.hands[player].cards:
                self.hands[player].remove(card)
            self.emit(use_event, extra_cards=[card])
            if self.pending_choose is not None:
                return True
            if self.pending_target is not None:
                self.pending_target.cancel = lambda: self.cancel_order(player, card, effective_cost)
                self.pending_target.finish = lambda: self.finish_order(player, card)
                return True
            self.hands[player].remove(card)
            self.discards[player].append(card)
            card.zone = Zone.DISCARD
            if not card.procedures:
                if card.effect is not None:
                    card.effect(self, player)
                elif card.heal_self:
                    self.hqs[player].df += card.cost
                else:
                    self.damage(self.hqs[player.opponent], card.cost, card, DamageType.NONE)
            self.check_victory()
            self.emit_use_after(player, card)
            return True
        return False

    def add_unit(
        self,
        player: Player,
        card: Card,
        index: int | None = None,
        line: Line | None = None,
    ) -> bool:
        """
        把一张单位直接加入场上, 用于效果召唤而与普通部署区分

        默认加入己方支援阵线最右侧
        传入前线时, 若前线被敌方占领则直接失败, 不会退回支援阵线
        TODO: 守护等关键词对加入位置的特殊规则

        Args:
            player: 控制者
            card: 单位
            index: 卡位位置, 缺省为最右侧
            line: 目标战线, 缺省为支援阵线

        Returns:
            是否加入成功
        """
        target = line if line is not None else self.support_lines[player]
        if not card.is_unit:
            return False
        if target.kind is LineKind.FRONT and target.owner not in (None, player):
            return False
        if len(target.units) >= target.capacity:
            return False
        for holder in (self.hands[player].cards, self.decks[player].cards, self.discards[player]):
            if card in holder:
                holder.remove(card)
        card.owner = player
        card.controller = player
        card.reset_state()
        card.revealed = False
        card.deployed_turn = self.turn_count
        target.add(card, index)
        card.zone = Zone.BOARD
        card.add_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
        self.emit(Event(EventType.ENTER, card=card, player=player, method=EntryMethod.ADD))
        return True

    def request_target(
        self,
        player: Player,
        source: Card,
        valid: Callable[[Card], bool],
        callback: Callable[[Card], None],
        cancel: Callable[[], None] | None = None,
    ) -> None:
        """
        进入指向状态, 等待玩家选择目标

        Args:
            player: 发起方
            source: 指向的来源卡牌
            valid: 目标合法性判断
            callback: 选定目标后的执行器
            cancel: 取消时的回调
        """
        self.pending_target = PendingTarget(player, source, valid, callback, cancel)

    def resolve_target(self, target: Card) -> bool:
        """
        结算指向目标

        Args:
            target: 选中的目标

        Returns:
            是否结算成功
        """
        pending = self.pending_target
        if pending is None or not pending.valid(target):
            return False
        self.pending_target = None
        self.emit(
            Event(
                EventType.TARGETED,
                target=target,
                source=pending.source,
                player=pending.player,
            )
        )
        pending.callback(target)
        if pending.finish is not None:
            pending.finish()
        return True

    def cancel_target(self) -> None:
        """取消当前指向, 并执行取消回调"""
        pending = self.pending_target
        self.pending_target = None
        if pending is not None and pending.cancel is not None:
            pending.cancel()

    def suppress(self, card: Card, until_turn_end: bool = False) -> None:
        """
        压制一个单位

        Args:
            card: 单位
            until_turn_end: 是否在本次回合结束时移除压制
        """
        if card.zone is not Zone.BOARD:
            return
        owner = card.controller
        card.suppressed = True
        card.suppressed_turn = self.turns_taken[owner]
        if until_turn_end:
            card.suppressed_until_turn = self.turn_count

    def extend_suppression(self, card: Card, turns: int = 1) -> None:
        """延长单位的压制时间。

        Args:
            card: 被压制的单位
            turns: 额外压制的回合数
        """
        if not card.suppressed:
            return
        if card.suppressed_until_turn >= 0:
            card.suppressed_until_turn += turns
        else:
            card.suppressed_turn += turns

    def start_card_choice(
        self,
        player: Player,
        cards: list[Card],
        source: Card,
        destination: Zone = Zone.HAND,
        develop: bool = False,
        origin_deck: bool = False,
        unselected_bottom: bool = False,
        loot_event: bool = False,
        title: str = "发现一张牌",
        callback: Callable[[Card, list[Card]], None] | None = None,
        next_turn: bool = False,
    ) -> bool:
        """
        开始一次三选一

        Args:
            player: 选取方
            cards: 候选卡牌, 超过三张时随机取三张
            destination: 选中后的区域
            develop: 是否触发 DEVELOP 事件
            origin_deck: 候选牌是否来自卡组
            unselected_bottom: 未选中的牌是否置于卡组底
            loot_event: 是否触发 LOOT 事件
            source: 来源卡牌
            title: 界面标题
            callback: 返回选中牌与未选中的两张牌

        Returns:
            是否成功开始
        """
        if self.pending_choice is not None or self.pending_selection is not None:
            return False
        if not cards:
            return False
        if len(cards) > 3:
            cards = random.sample(cards, 3)
        self.last_choice_result = None
        self.pending_choice = CardChoice(
            player,
            cards,
            source,
            destination,
            develop,
            origin_deck,
            unselected_bottom,
            loot_event,
            title,
            callback,
            next_turn,
        )
        if self.kind_of(player) is PlayerKind.AI or player is Player.B:
            self.resolve_random_choice()
        return True

    def start_choose(
        self,
        player: Player,
        source: Card,
        options: list[ChooseOption],
    ) -> bool:
        """
        开始一次抉择。

        Args:
            player: 抉择方
            source: 来源卡牌
            options: 两个选项

        Returns:
            是否成功开始
        """
        if self.pending_choose is not None or self.pending_choice is not None:
            return False
        if len(options) != 2:
            return False
        self.pending_choose = ChooseRequest(player, source, options, source.effective_cost)
        if self.kind_of(player) is PlayerKind.AI or player is Player.B:
            self.resolve_choose(random.choice(options))
        return True

    def resolve_choose(self, option: ChooseOption) -> bool:
        """
        结算抉择选项。

        Args:
            option: 选中的选项

        Returns:
            是否结算成功
        """
        request = self.pending_choose
        if request is None or option not in request.options:
            return False
        self.pending_choose = None
        source = request.source
        self.kredits[request.player].spend(request.cost)
        if source in self.hands[request.player].cards:
            self.hands[request.player].remove(source)
        if source not in self.discards[request.player]:
            self.discards[request.player].append(source)
        source.zone = Zone.DISCARD
        option.action()
        self.emit_use_after(request.player, source)
        return True

    def cancel_choose(self) -> bool:
        """
        取消抉择，把来源卡牌放回手中。

        Returns:
            是否取消成功
        """
        request = self.pending_choose
        if request is None:
            return False
        self.pending_choose = None
        self.move_to_hand(request.source, request.player)
        hand = self.hands[request.player]
        if request.hand_index >= 0 and request.source in hand.cards:
            hand.cards.remove(request.source)
            hand.cards.insert(min(request.hand_index, len(hand.cards)), request.source)
        return True

    def unit_combat(self, attacker: Card, defender: Card) -> None:
        """
        两个单位互相造成等同于自身攻击力的战斗伤害。

        Args:
            attacker: 单位 A
            defender: 单位 B
        """
        if not attacker.is_unit or not defender.is_unit:
            return
        attacker_at = attacker.at
        defender_at = defender.at
        self.damage(attacker, defender_at, defender, DamageType.BATTLE)
        self.damage(defender, attacker_at, attacker, DamageType.BATTLE)

    def shadow_hq(self, player: Player) -> Card:
        """
        返回玩家的影子总部, 不存在时创建

        Args:
            player: 玩家

        Returns:
            影子总部
        """
        hq = self.shadow_hqs[player]
        if hq is None:
            hq = Card(
                type=CardType.HQ,
                cost=0,
                name="shadow_hq",
                country=Country.NEUTRAL,
                at=0,
                df=1,
                display_name="影子总部",
            )
            hq.owner = player
            hq.controller = player
            hq.zone = Zone.REMOVED
            self.shadow_hqs[player] = hq
        return hq

    def start_shadow_timer(
        self,
        player: Player,
        action: Callable[[], None],
        turns: int = 1,
    ) -> None:
        """
        给影子总部添加计时器

        Args:
            player: 计时器所有者
            action: 归零时执行的动作
            turns: 初始回合数
        """
        self.shadow_hq(player)
        self.shadow_timers[player].append(ShadowTimer(turns, action))

    def _resolve_auto_target(self) -> None:
        """自动使用卡牌时, 自动选择第一个合法目标"""
        pending = self.pending_target
        if pending is None:
            return
        target = next((item for item in self.targets if pending.valid(item)), None)
        if target is None:
            self.cancel_target()
            return
        self.resolve_target(target)

    def auto_use_card(self, card: Card, player: Player) -> bool:
        """
        自动使用进入手牌的 PFWD 卡牌

        Args:
            card: 进入手牌的卡牌
            player: 获得方

        Returns:
            是否自动使用
        """
        if card.zone is not Zone.HAND or not card.has_keyword("pfwd"):
            return False
        if card.sub_type == "weather" and self.weather_used_turn[player] == self.turn_count:
            return False
        card.owner = player
        card.controller = player
        if card.sub_type == "weather":
            self.weather_used_turn[player] = self.turn_count
        if card.is_unit:
            line = self.support_lines[player]
            if len(line.units) >= line.capacity:
                return False
            self.hands[player].remove(card)
            operation_cost = card.operation_cost
            card.reset_state()
            card.operation_cost = operation_cost
            card.revealed = False
            card.deployed_turn = self.turn_count
            line.add(card)
            card.zone = Zone.BOARD
            card.add_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
            self.targets = self.all_targets()
            self.emit(
                Event(
                    EventType.USE,
                    card=card,
                    source=card,
                    player=player,
                    targets=[],
                    method=EntryMethod.DEPLOY,
                )
            )
            self._resolve_auto_target()
            for hook in DEPLOY_FALLBACK_HOOKS:
                hook(self, player, card)
            if card.zone is Zone.BOARD:
                self.emit(
                    Event(
                        EventType.ENTER,
                        card=card,
                        player=player,
                        method=EntryMethod.DEPLOY,
                    )
                )
            return True
        # 指令: 忽略费用和回合限制, 直接触发效果
        card.zone = Zone.HAND
        self.targets = self.all_targets()
        self.emit(
            Event(
                EventType.USE,
                card=card,
                source=card,
                player=player,
                targets=list(self.targets),
            )
        )
        self._resolve_auto_target()
        if card in self.hands[player].cards:
            self.hands[player].remove(card)
        card.zone = Zone.DISCARD
        if card not in self.discards[player]:
            self.discards[player].append(card)
        self.emit_use_after(player, card)
        self.check_victory()
        return True

    def move_to_hand(self, card: Card, player: Player) -> bool:
        """
        将卡牌移入玩家手牌

        Args:
            card: 要移动的卡牌
            player: 目标玩家

        Returns:
            是否成功进入手牌
        """
        for holder in (
            self.hands[player].cards,
            self.decks[player].cards,
            self.discards[player],
        ):
            if card in holder:
                holder.remove(card)
        if card.line is not None:
            card.line.remove(card)
        card.owner = player
        card.controller = player
        card.zone = Zone.HAND
        card.revealed = False
        if self.hands[player].add(card):
            self.emit(Event(EventType.ADD_TO_HAND, card=card, player=player))
            self.auto_use_card(card, player)
            return True
        self.discard_card(player, card)
        return False

    def resolve_card_choice(self, card: Card) -> bool:
        """
        确认三选一

        Args:
            card: 选中的卡牌

        Returns:
            是否结算成功
        """
        choice = self.pending_choice
        if choice is None or card not in choice.cards:
            return False
        self.pending_choice = None
        if choice.next_turn:
            # 预报选中的天气延迟到下个友方回合开始
            for holder in (
                self.hands[choice.player].cards,
                self.decks[choice.player].cards,
                self.discards[choice.player],
            ):
                if card in holder:
                    holder.remove(card)
            card.owner = choice.player
            card.zone = Zone.REMOVED
            card_id = card.card_id
            owner = choice.player

            def add_weather() -> None:
                self.give_card(owner, card_id, Zone.HAND, revealed=False)

            self.start_shadow_timer(owner, add_weather)
        elif choice.destination is Zone.HAND:
            self.move_to_hand(card, choice.player)
        else:
            for holder in (
                self.hands[choice.player].cards,
                self.decks[choice.player].cards,
                self.discards[choice.player],
            ):
                if card in holder:
                    holder.remove(card)
            card.owner = choice.player
            if choice.destination is Zone.DECK:
                self.decks[choice.player].cards.insert(
                    random.randint(0, len(self.decks[choice.player].cards)),
                    card,
                )
                card.zone = Zone.DECK
                card.revealed = False
            elif choice.destination is Zone.BOARD:
                self.add_unit(choice.player, card)
        for other in choice.cards:
            if other is card:
                continue
            if choice.origin_deck:
                if choice.unselected_bottom:
                    self.decks[choice.player].cards.insert(0, other)
                else:
                    self.decks[choice.player].cards.insert(
                        random.randint(0, len(self.decks[choice.player].cards)),
                        other,
                    )
                other.zone = Zone.DECK
                other.revealed = False
            else:
                self.discards[choice.player].append(other)
                other.zone = Zone.DISCARD
        if choice.origin_deck and not choice.unselected_bottom:
            self.shuffle_deck(choice.player)
        remaining = [other for other in choice.cards if other is not card]
        self.last_choice_result = (card, remaining)
        if choice.develop:
            self.emit(
                Event(
                    EventType.DEVELOP,
                    card=card,
                    player=choice.player,
                    source=choice.source,
                )
            )
        if choice.loot_event:
            self.emit(
                Event(
                    EventType.LOOT,
                    card=card,
                    player=choice.player,
                    source=choice.source,
                )
            )
        if choice.callback is not None:
            choice.callback(card, remaining)
        self.emit(
            Event(EventType.CHOICE_RESOLVED, card=card, player=choice.player, source=choice.source)
        )
        return True

    def resolve_random_choice(self) -> bool:
        """随机确认当前三选一"""
        choice = self.pending_choice
        if choice is None or not choice.cards:
            return False
        return self.resolve_card_choice(random.choice(choice.cards))

    def develop_from_deck(self, player: Player, source: Card) -> bool:
        """
        从卡组随机展示三张牌, 选择一张加入手牌

        Args:
            player: 玩家
            source: 开发来源

        Returns:
            是否成功开始
        """
        deck_cards = self.decks[player].cards
        if not deck_cards:
            return False
        targets = random.sample(deck_cards, min(3, len(deck_cards)))
        for card in targets:
            deck_cards.remove(card)
        return self.start_card_choice(
            player,
            targets,
            source,
            destination=Zone.HAND,
            develop=True,
            origin_deck=True,
            title="发现：开发",
        )

    def develop_from_pool(self, player: Player, source: Card) -> bool:
        """
        从当前卡组中随机展示三张牌, 选择一张加入手牌

        开发不会移除卡组中的牌:
        它只读取卡组里存在的卡牌 id, 生成额外的卡牌实例作为选项。
        因此开发池不会出现玩家卡组以外的卡牌。

        Args:
            player: 玩家
            source: 开发来源

        Returns:
            是否成功开始
        """
        deck_ids = {
            card.card_id
            for card in self.decks[player].cards
            if card.card_id
        }
        candidates: list[str] = []
        for card_id in deck_ids:
            data = cards.get(card_id)
            if data is None:
                continue
            if CardTag.NOT_IN_START in data.tags:
                continue
            if data.type is CardType.HQ:
                continue
            candidates.append(card_id)
        if not candidates:
            return False
        chosen_ids = random.sample(candidates, min(3, len(candidates)))
        # 构筑外副本: 不修改原卡组, 选项是独立卡牌实例
        choices = [cards.create(card_id) for card_id in chosen_ids]
        for card in choices:
            card.owner = player
            card.controller = player
            card.zone = Zone.DECK
        return self.start_card_choice(
            player,
            choices,
            source,
            destination=Zone.HAND,
            develop=True,
            origin_deck=False,
            title="发现：开发",
        )

    def loot_from_deck(self, player: Player, source: Card) -> bool:
        """
        从卡组顶三张牌中选择一张加入手牌

        Args:
            player: 玩家
            source: 来源

        Returns:
            是否成功开始
        """
        deck_cards = self.decks[player].cards
        if not deck_cards:
            return False
        targets = list(deck_cards[-3:])
        for card in targets:
            deck_cards.remove(card)
        return self.start_card_choice(
            player,
            targets,
            source,
            destination=Zone.HAND,
            origin_deck=True,
            unselected_bottom=True,
            loot_event=True,
            title="发现：战利品",
        )

    def start_selection(
        self,
        player: Player,
        min_count: int,
        max_count: int,
        callback: Callable[[list[Card]], None],
        filter: Callable[[Card], bool] | None = None,
        title: str = "选取手牌",
    ) -> bool:
        """
        开始一次手牌选取

        Args:
            player: 发起方
            min_count: 最少选取数量
            max_count: 最多选取数量
            callback: 确认后的回调
            filter: 可选筛选器
            title: 提示文本

        Returns:
            是否成功开始
        """
        if self.pending_selection is not None:
            return False
        if self.pending_choice is not None:
            return False
        if min_count < 0 or max_count < min_count:
            return False
        available = [
            card
            for card in self.hands[player].cards
            if filter is None or filter(card)
        ]
        if len(available) < min_count:
            return False
        self.pending_selection = SelectionRequest(
            player,
            min_count,
            max_count,
            callback,
            filter,
            title,
        )
        return True

    def resolve_selection(self, cards: list[Card]) -> bool:
        """
        确认当前手牌选取
            Args:
            cards: 选中的手牌

        Returns:
            是否结算成功
        """
        request = self.pending_selection
        if request is None:
            return False
        if not (request.min_count <= len(cards) <= request.max_count):
            return False
        for card in cards:
            if card not in self.hands[request.player].cards:
                return False
            if request.filter is not None and not request.filter(card):
                return False
        self.pending_selection = None
        request.callback(list(cards))
        return True

    def cancel_selection(self) -> None:
        """取消当前手牌选取"""
        self.pending_selection = None

    def start_mulligan(self, player: Player) -> bool:
        """
        开始开局重新调度: 选取 0~5 张手牌洗回卡组并抽等量牌

        Args:
            player: 玩家

        Returns:
            是否成功开始
        """
        max_count = min(5, len(self.hands[player].cards))
        if max_count <= 0:
            return False
        return self.start_selection(
            player,
            0,
            max_count,
            lambda cards: self._apply_mulligan(player, cards),
            title="重新调度：选取要替换的手牌",
        )

    def _apply_mulligan(self, player: Player, cards: list[Card]) -> None:
        """
        将选取的手牌洗回卡组并抽取等量卡牌

        Args:
            player: 玩家
            cards: 选中的手牌
        """
        for card in cards:
            if card in self.hands[player].cards:
                self.hands[player].remove(card)
            self.decks[player].cards.insert(
                random.randint(0, len(self.decks[player].cards)),
                card,
            )
            card.zone = Zone.DECK
            card.revealed = False
            self.emit(
                Event(
                    EventType.ADD_TO_DECK,
                    card=card,
                    player=player,
                    index=len(self.decks[player].cards) - 1,
                )
            )
        if cards:
            count = len(cards)
            self.schedule_action(560, lambda: self.shuffle_deck(player))

            special_source = self.special_source(player)

            def draw_replacement() -> None:
                for _ in range(count):
                    self.draw(player, special_source)

            self.schedule_action(1200, draw_replacement)

    def cancel_deploy(
        self,
        player: Player,
        card: Card,
        cost: int,
        refund: bool = True,
    ) -> None:
        """
        取消一次部署, 把单位收回手牌；按需退还费用

        Args:
            player: 部署方
            card: 被部署的单位
            cost: 部署花费
            refund: 是否退还费用；指向部署在选目标前尚未扣费
        """
        if card.line is not None:
            card.line.remove(card)
        self.hands[player].add(card)
        card.zone = Zone.HAND
        card.deployed_turn = -1
        card.remove_tag(CardTag.CANNOT_ACT_WHEN_ENTER)
        # 收回手牌时清除部署期间获得的光环和临时属性
        card.clear_auras()
        card.clear_temporary()
        if refund:
            self.kredits[player].credits = min(
                self.kredits[player].credits + cost,
                self.kredits[player].slots,
            )

    def emit_use_after(self, player: Player, card: Card) -> None:
        """广播指令效果结算完成事件。

        Args:
            player: 使用者
            card: 已结算的指令
        """
        self.emit(
            Event(
                EventType.USE_AFTER,
                card=card,
                source=card,
                player=player,
                targets=list(self.targets),
            )
        )

    def finish_order(self, player: Player, card: Card) -> None:
        """
        指向型指令结算完成, 从手牌进入弃牌堆

        Args:
            player: 使用方
            card: 指令
        """
        if card in self.hands[player].cards:
            self.hands[player].remove(card)
        self.discards[player].append(card)
        card.zone = Zone.DISCARD
        self.emit_use_after(player, card)
        self.check_victory()

    def cancel_order(self, player: Player, card: Card, cost: int) -> None:
        """
        取消一次指向型指令, 保留在手牌并退还费用

        Args:
            player: 使用方
            card: 被取消的指令
            cost: 指令花费
        """
        if card in self.discards[player]:
            self.discards[player].remove(card)
        if card not in self.hands[player].cards:
            self.hands[player].add(card)
        card.zone = Zone.HAND
        self.kredits[player].credits = min(self.kredits[player].credits + cost, self.kredits[player].slots)

    def remove_unit(self, card: Card, source: Card) -> None:
        """
        将单位从战场移除(非消灭), 进入移除区

        Args:
            card: 单位
            source: 效果来源
        """
        player = card.controller
        line = card.line
        if line is not None:
            line.remove(card)
            if line.kind is LineKind.FRONT and not line.units:
                line.owner = None
        card.zone = Zone.REMOVED
        self.emit(
            Event(
                EventType.LEAVE,
                card=card,
                player=player,
                way=LeaveMethod.REMOVED,
                source=source,
            )
        )

    def discard_card(self, player: Player, card: Card) -> None:
        """
        弃掉一张卡牌, 进入弃牌堆并发 DISCARD 事件

        Args:
            player: 所属玩家
            card: 被弃掉的卡牌
        """
        if card in self.hands[player].cards:
            self.hands[player].remove(card)
        if card not in self.discards[player]:
            self.discards[player].append(card)
        card.zone = Zone.DISCARD
        self.emit(Event(EventType.DISCARD, card=card, player=player))

    def units_in_effect_order(self, player: Player) -> list[Card]:
        """
        按效果结算顺序返回场上单位: 敌方支援阵线 -> 前线 -> 友方支援阵线
        每条阵线内从右到左

        Args:
            player: 效果发起方

        Returns:
            单位列表
        """
        result: list[Card] = []
        for line in (
            self.support_lines[player.opponent],
            self.front_line,
            self.support_lines[player],
        ):
            result.extend(reversed(line.units))
        return result

    def inhibit_unit(self, card: Card, source: Card) -> None:
        """
        抑制单位: 移除全部效果和关键词, 重置攻击力/最大防御力/行动花费

        Args:
            card: 单位
            source: 效果来源
        """
        if card.has_tag(CardTag.UNINHIBITABLE):
            return
        card.inhibited = True
        card.keywords.clear()
        card.aura_keywords.clear()
        card.procedures.clear()
        card.tags.clear()
        card.base_tags.clear()
        card.keyword_values.clear()
        card.effect = None
        card.at = card.initial_at
        card.max_df = card.initial_df
        card.df = min(card.df, card.max_df)
        card.operation_cost = card.initial_operation_cost
        card.clear_auras()

    def retreat_unit(self, card: Card, source: Card) -> None:
        """
        撤退单位: 前线单位返回支援阵线, 已在支援阵线或支援阵线已满时返回手牌

        撤退不计入行动或移动

        Args:
            card: 单位
            source: 效果来源
        """
        if not card.is_unit or card.zone is not Zone.BOARD:
            return
        player = card.controller
        line = card.line
        if line is not None and line.kind is LineKind.FRONT:
            support = self.support_lines[player]
            if len(support.units) < support.capacity:
                line.remove(card)
                support.add(card)
                card.zone = Zone.BOARD
                self.emit(
                    Event(
                        EventType.RETREAT,
                        card=card,
                        player=player,
                        source=source,
                    )
                )
                return
        self.return_unit(card, source)

    def return_unit(self, card: Card, source: Card) -> None:
        """
        将单位返回所有者手中, 并重置为初始状态

        手牌已满时改为弃掉该单位

        Args:
            card: 单位
            source: 效果来源
        """
        player = card.controller
        line = card.line
        if line is not None:
            line.remove(card)
            if line.kind is LineKind.FRONT and not line.units:
                line.owner = None
        card.reset_state(clear_modifiers=True)
        card.revealed = True
        if self.hands[player].add(card):
            card.zone = Zone.HAND
        else:
            self.discard_card(player, card)
        self.emit(
            Event(
                EventType.LEAVE,
                card=card,
                player=player,
                way=LeaveMethod.RETURN_HAND,
                source=source,
            )
        )

    def shuffle_deck(self, player: Player) -> None:
        """
        随机打乱玩家卡组并发出洗切事件

        Args:
            player: 玩家
        """
        random.shuffle(self.decks[player].cards)
        self.emit(Event(EventType.SHUFFLE, player=player))

    def add_to_deck_and_shuffle(self, player: Player, card_id: str) -> Card | None:
        """
        将一张卡加入卡组后洗切

        Args:
            player: 玩家
            card_id: 卡牌 id

        Returns:
            加入的卡牌, 失败时为 None
        """
        card = self.give_card(player, card_id, Zone.DECK)
        if card is not None:
            self.shuffle_deck(player)
        return card

    def put_card_into_deck(self, player: Player, card: Card) -> None:
        """
        将一张手牌洗入卡组并洗切

        Args:
            player: 玩家
            card: 卡牌
        """
        if card in self.hands[player].cards:
            self.hands[player].remove(card)
        card.reset_state(clear_modifiers=True)
        card.revealed = False
        deck_cards = self.decks[player].cards
        position = random.randint(0, len(deck_cards))
        deck_cards.insert(position, card)
        card.zone = Zone.DECK
        self.emit(Event(EventType.ADD_TO_DECK, card=card, player=player, index=position))
        self.schedule_action(560, lambda: self.shuffle_deck(player))

    def isolate_card(
        self,
        player: Player,
        card: Card,
        source: Card,
    ) -> bool:
        """
        移除一个单位, 并在该玩家下个回合开始时返回

        Args:
            player: 使用孤立的一方
            card: 被移除的单位
            source: 效果来源

        Returns:
            是否成功移除
        """
        if card.zone is not Zone.BOARD or not card.is_unit:
            return False
        if card.line is not None:
            card.line.remove(card)
        card.zone = Zone.REMOVED
        self.pending_isolated.append((card, player))
        self.emit(
            Event(
                EventType.LEAVE,
                card=card,
                player=player,
                way=LeaveMethod.REMOVED,
                source=source,
            )
        )
        return True

    def schedule_return(self, card: Card, source: Card, delay_ms: int) -> None:
        """
        延迟将单位返回手牌, 用于逐个结算

        Args:
            card: 单位
            source: 效果来源
            delay_ms: 延迟毫秒数
        """
        self.pending_returns.append((pygame.time.get_ticks() + delay_ms, card, source))

    @property
    def add_deck_delay(self) -> int:
        """加入卡组动画延迟, 毫秒"""
        return (
            Global.save_data.add_deck_delay
            if Global.save_data is not None
            else DEFAULT_ADD_DECK_DELAY
        )

    def schedule_action(self, delay_ms: int, action: Callable[[], None]) -> None:
        """
        延迟执行一个动作

        Args:
            delay_ms: 延迟毫秒数
            action: 要执行的动作
        """
        self.pending_actions.append((pygame.time.get_ticks() + delay_ms, action))

    def give_card(
        self,
        player: Player,
        card_id: str,
        zone: Zone,
        index: int | None = None,
        line: Line | None = None,
        revealed: bool = True,
    ) -> Card | None:
        """
        将一张指定卡牌加入指定区域

        加入的卡牌默认带 NOT_IN_START 标签
        BOARD 默认从支援阵线最右侧加入, 可以指定前线

        Args:
            player: 获得方
            card_id: 卡牌 id
            zone: 目标区域, 支持 HAND/DECK/BOARD
            index: 卡组或战线中的插入位置, 卡组缺省为随机位置
            line: 加入场上时的目标战线, 缺省为支援阵线
            revealed: 加入手牌时是否为明牌

        Returns:
            加入的卡牌, 失败时为 None
        """
        if not cards.has(card_id):
            logger.warning("给牌失败, 未注册的卡牌: %s", card_id)
            return None
        card = cards.create(card_id)
        card.owner = player
        card.revealed = revealed if zone is Zone.HAND else False
        card.add_tag(CardTag.NOT_IN_START)
        if zone is Zone.HAND:
            if not self.hands[player].add(card):
                self.discards[player].append(card)
                card.zone = Zone.DISCARD
                self.emit(Event(EventType.ADD_TO_HAND, card=card, player=player))
                return card
            card.zone = Zone.HAND
            self.emit(Event(EventType.ADD_TO_HAND, card=card, player=player))
            self.auto_use_card(card, player)
            return card
        if zone is Zone.DECK:
            deck_cards = self.decks[player].cards
            position = random.randint(0, len(deck_cards)) if index is None else max(0, min(index, len(deck_cards)))
            deck_cards.insert(position, card)
            card.zone = Zone.DECK
            self.emit(Event(EventType.ADD_TO_DECK, card=card, player=player, index=position))
            return card
        if zone is Zone.BOARD:
            if not self.add_unit(player, card, index, line):
                return None
            self.emit(Event(EventType.ADD_TO_BOARD, card=card, player=player))
            return card
        logger.warning("给牌失败, 不支持的区域: %s", zone)
        return None

    def move_unit(self, player: Player, card: Card, line: Line, index: int | None = None) -> bool:
        """
        移动单位到目标战线

        Args:
            player: 操作者
            card: 单位
            line: 目标战线
            index: 目标位置

        Returns:
            是否移动成功
        """
        if player is not self.turn_owner:
            return False
        if card.controller is not player or not self.can_move_now(card):
            return False
        if not self.kredits[player].can_afford(card.operation_cost):
            return False
        if not card.move(line, index):
            return False
        self.kredits[player].spend(card.operation_cost)
        card.moved_turn = self.turn_count
        card.add_tag(CardTag.MOVED)
        self.emit(Event(EventType.MOVE, card=card, player=player, line=line))
        return True

    def attack_unit(self, player: Player, card: Card, target: Card) -> bool:
        """
        单位攻击目标, 结算反击

        Args:
            player: 攻击方
            card: 攻击单位
            target: 目标单位或总部

        Returns:
            是否攻击成功
        """
        if player is not self.turn_owner:
            return False
        if card.controller is not player or not self.can_attack_now(card):
            return False
        if not self.can_attack(player, card, target):
            return False
        if not self.kredits[player].can_afford(card.operation_cost):
            return False
        self.kredits[player].spend(card.operation_cost)
        card.attacked_turn = self.turn_count
        card.attacks_turn += 1
        card.add_tag(CardTag.ATTACKED)
        kind = DamageType.HQ_ATTACK if target.is_hq else DamageType.ATTACK
        target_unit = target.is_unit
        counter_at = target.at
        counter = target_unit and self.counter_damage(card, target)
        ambush_immune = False
        if (
            counter
            and target.has_keyword("ambush")
            and target.ambush_used_turn != self.turn_count
        ):
            target.ambush_used_turn = self.turn_count
            counter_damage = max(0, counter_at - min(max(card.armor, 0), 3))
            if counter_damage >= card.df:
                ambush_immune = True
        self.emit(Event(EventType.ATTACK, card=card, target=target, player=player))
        if not ambush_immune:
            self.damage(target, card.at, card, kind)
        if (
            target.zone is Zone.DISCARD
            and card.has_tag(CardTag.OVERFLOW_DAMAGE)
        ):
            overflow = target.overflow_damage
            if overflow > 0:
                self.damage(self.hqs[player.opponent], overflow, card, DamageType.NONE)
        if counter:
            self.damage(card, counter_at, target, DamageType.COUNTER)
        if (
            target.zone is Zone.DISCARD
            and card.zone is Zone.BOARD
            and card.has_tag(CardTag.REFRESH_ON_KILL)
        ):
            card.attacks_turn = 0
            card.remove_tag(CardTag.ATTACKED)
            card.remove_tag(CardTag.MOVED)
            card.attacked_turn = -1
            card.moved_turn = -1
        return True

    def counter_damage(self, attacker: Card, defender: Card) -> bool:
        """
        判断本次交战是否会触发反击

        炮兵不会受到反击伤害; 轰炸机不会造成反击伤害
        轰炸机作为攻击方时只会受到战斗机造成的反击伤害

        Args:
            attacker: 攻击方
            defender: 防御方

        Returns:
            是否触发反击
        """
        if attacker.has_keyword("shock"):
            return False
        if defender.type is CardType.BOMBER:
            return False
        if attacker.type is CardType.ARTILLERY:
            return False
        if attacker.type is CardType.BOMBER:
            return defender.type is CardType.FIGHTER
        return True

    def check_victory(self) -> Player | None:
        """
        检查胜负, 双方同时归零则回合所有者失败

        Returns:
            胜方, 未分出胜负时为 None
        """
        if self.winner is not None:
            return self.winner
        a_dead = self.hqs[Player.A].df <= 0
        b_dead = self.hqs[Player.B].df <= 0
        if a_dead and b_dead:
            self.winner = self.turn_owner.opponent
        elif a_dead:
            self.winner = Player.B
        elif b_dead:
            self.winner = Player.A
        return self.winner

# ==================== Mod 加载 ====================


def _load_module(module_name: str, path: Path) -> Any:
    """
    按包路径加载模块, 失败时退回按文件路径加载

    Args:
        module_name: 模块名, 例如 mods.kards.cards.xxx
        path: 文件路径

    Returns:
        加载的模块, 失败时返回 None
    """
    import importlib
    import importlib.util
    sys.modules.setdefault("main", sys.modules[__name__])
    package_root = str(Path(__file__).resolve().parent)
    if package_root not in sys.path:
        sys.path.insert(0, package_root)
    sys.modules.pop(module_name, None)
    try:
        return importlib.import_module(module_name)
    except ImportError:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _read_mod_info(mod_dir: Path, mod_id: str) -> ModInfo:
    """
    读取 mod 的 info.json 元信息

    Args:
        mod_dir: mod 目录
        mod_id: mod 标识, 作为缺省显示名称

    Returns:
        mod 元信息, 缺失或无效时返回默认值
    """
    default: ModInfo = {
        "name": mod_id,
        "version": "",
        "author": "",
        "description": "",
        "dependencies": [],
    }
    info_file = mod_dir / "info.json"
    if not info_file.is_file():
        return default
    try:
        parsed: object = json.loads(info_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        logger.warning(f"info.json 读取失败 {mod_id}: {exc}")
        return default
    if not isinstance(parsed, dict):
        return default
    raw = _string_dict(parsed)
    dependencies_raw = raw.get("dependencies", [])
    dependencies = [str(item) for item in _object_list(dependencies_raw)]
    return {
        "name": str(raw.get("name", mod_id)),
        "version": str(raw.get("version", "")),
        "author": str(raw.get("author", "")),
        "description": str(raw.get("description", "")),
        "dependencies": dependencies,
    }


def _resolve_load_order(dirs: dict[str, Path], infos: dict[str, ModInfo]) -> list[str]:
    """
    按依赖关系计算 mod 加载顺序

    Args:
        dirs: mod id 到目录的映射
        infos: mod id 到元信息的映射

    Returns:
        可加载的 mod id 顺序
    """
    order: list[str] = []
    done: set[str] = set()
    visiting: set[str] = set()

    def visit(mod_id: str, chain: list[str]) -> None:
        if mod_id in done:
            return
        if mod_id in visiting:
            logger.error("mod 依赖成环: %s", " -> ".join(chain + [mod_id]))
            return
        visiting.add(mod_id)
        for dependency in infos[mod_id]["dependencies"]:
            if dependency not in dirs:
                logger.warning("mod %s 缺少依赖 %s, 已跳过", mod_id, dependency)
                visiting.discard(mod_id)
                return
            visit(dependency, chain + [mod_id])
            if dependency not in done:
                logger.warning("mod %s 的依赖 %s 未加载, 已跳过", mod_id, dependency)
                visiting.discard(mod_id)
                return
        visiting.discard(mod_id)
        done.add(mod_id)
        order.append(mod_id)

    for mod_id in dirs:
        visit(mod_id, [])
    return order


def _load_mod(mod_dir: Path, mod_id: str, info: ModInfo) -> None:
    """
    加载单个 mod 的关键词、中文数据与卡牌

    Args:
        mod_dir: mod 目录
        mod_id: mod 标识
        info: mod 元信息
    """
    cards.mods[mod_id] = info
    code_dir = mod_dir / "code"
    keywords_dir = code_dir / "keywords"
    if keywords_dir.is_dir():
        registry: object = None
        init_file = keywords_dir / "__init__.py"
        if init_file.is_file():
            package = _load_module(f"mods.{mod_id}.code.keywords", init_file)
            registry = getattr(package, "KEYWORDS", None)
        if isinstance(registry, dict):
            for keyword_id, keyword in _string_dict(registry).items():
                if not isinstance(keyword, KeywordData):
                    logger.warning(f"关键词注册表项无效: {keyword_id}")
                    continue
                keyword.keyword_id = keyword_id
                cards.keywords[keyword_id] = keyword
                cards.keyword_names[keyword_id] = keyword.name
        else:
            for kw_file in sorted(keywords_dir.glob("*.py")):
                if kw_file.stem.startswith("_"):
                    continue
                kw_module = _load_module(f"mods.{mod_id}.code.keywords.{kw_file.stem}", kw_file)
                keyword = getattr(kw_module, "KEYWORD", None)
                if not isinstance(keyword, KeywordData):
                    logger.warning(f"关键词文件缺少 KEYWORD: {kw_file.name}")
                    continue
                keyword.keyword_id = kw_file.stem
                cards.keywords[keyword.keyword_id] = keyword
                cards.keyword_names[keyword.keyword_id] = keyword.name
    else:
        legacy = code_dir / "keywords.py"
        if legacy.is_file():
            legacy_module = _load_module(f"mods.{mod_id}.code.keywords", legacy)
            extra = getattr(legacy_module, "KEYWORDS", None)
            if isinstance(extra, dict):
                for key, value in _string_dict(extra).items():
                    if isinstance(value, str):
                        cards.keyword_names[key] = value
    zh_file = mod_dir / "data" / "zh.json"
    if zh_file.is_file():
        try:
            zh_data: object = json.loads(zh_file.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            logger.warning(f"zh.json 读取失败 {mod_id}: {exc}")
        else:
            if isinstance(zh_data, dict):
                for key, value in _string_dict(zh_data).items():
                    if isinstance(value, dict):
                        cards.zh[key] = _string_dict(value)
    hooks_file = code_dir / "hooks.py"
    if hooks_file.is_file():
        _load_module(f"mods.{mod_id}.code.hooks", hooks_file)
    cards_dir = code_dir / "cards"
    if not cards_dir.is_dir():
        return
    for py_file in sorted(cards_dir.rglob("*.py")):
        if py_file.stem.startswith("_"):
            continue
        module = _load_module(f"mods.{mod_id}.code.cards.{py_file.stem}", py_file)
        card = getattr(module, "CARD_DATA", None)
        if not isinstance(card, CardData):
            logger.warning(f"卡牌文件缺少 CARD_DATA: {py_file.name}")
            continue
        card.name = py_file.stem
        card.card_id = f"{mod_id}:{py_file.stem}"
        db_id = py_file.stem.removeprefix("card_")
        entry = cards.zh.get(db_id)
        if entry is not None:
            card.display_name = str(entry.get("title", "")) or card.display_name
            card.text = str(entry.get("text", "")) or card.text
        cards.add(card)


def _normalize_element_path(
    path: str,
    default_mod: str,
    known_mods: set[str],
) -> tuple[str | None, str, str] | None:
    """
    解析 replace.json 中的元素路径

    支持:
        cards/Germany/card_a
        code/cards/Germany/card_a.py
        modB/code/cards/Germany/card_b.py
        keywords/armor
        modB:card_b

    Returns:
        (mod_id, kind, stem), 无法解析时为 None
    """
    text = path.strip().replace("\\", "/").strip("/")
    if ":" in text:
        mod_id, stem = text.split(":", 1)
        return mod_id or default_mod, "cards", Path(stem).stem
    parts = [part for part in text.split("/") if part]
    if parts and parts[0] == "mods":
        parts.pop(0)
    mod_id: str | None = None
    if parts and parts[0] in known_mods:
        mod_id = parts.pop(0)
    if parts and parts[0] == "code":
        parts.pop(0)
    if len(parts) < 2 or parts[0] not in ("cards", "keywords"):
        logger.warning("无法解析替换路径: %s", path)
        return None
    kind = parts[0]
    return mod_id or default_mod, kind, Path(parts[-1]).stem


def _apply_replacements(mod_dirs: dict[str, Path]) -> None:
    """读取每个 mod 的 replace.json, 将 B 的元素替换为 A 的元素"""
    known = set(mod_dirs)
    for mod_id, mod_dir in mod_dirs.items():
        replace_file = mod_dir / "replace.json"
        if not replace_file.is_file():
            continue
        try:
            data = json.loads(replace_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("replace.json 读取失败: %s", replace_file)
            continue
        if not isinstance(data, dict):
            continue
        for source_path, target_path in _string_dict(data).items():
            source = _normalize_element_path(source_path, mod_id, known)
            target = _normalize_element_path(target_path, "", known)
            if source is None or target is None:
                continue
            source_mod, kind, source_stem = source
            target_mod, _, target_stem = target
            if source_mod is None:
                source_mod = mod_id
            if kind == "cards":
                source_id = f"{source_mod}:{source_stem}"
                source_card = cards.get(source_id)
                if source_card is None:
                    logger.warning("替换源卡牌不存在: %s", source_id)
                    continue
                target_id = f"{target_mod}:{target_stem}"
                if not target_mod:
                    candidates = [
                        f"{candidate_mod}:{target_stem}"
                        for candidate_mod in known
                        if cards.get(f"{candidate_mod}:{target_stem}") is not None
                    ]
                    if not candidates:
                        logger.warning("替换目标卡牌不存在: %s", target_stem)
                        continue
                    target_id = candidates[0]
                if cards.get(target_id) is None:
                    logger.warning("替换目标卡牌不存在: %s", target_id)
                    continue
                cards.replace(target_id, source_card)
                logger.info("卡牌替换: %s -> %s", target_id, source_id)
            else:
                source_keyword = cards.keywords.get(source_stem)
                if source_keyword is None:
                    logger.warning("替换源关键词不存在: %s", source_stem)
                    continue
                if target_stem not in cards.keywords:
                    logger.warning("替换目标关键词不存在: %s", target_stem)
                    continue
                cards.keywords[target_stem] = source_keyword
                logger.info("关键词替换: %s -> %s", target_stem, source_stem)


def load_mods() -> None:
    """
    扫描 mods 目录, 按依赖顺序加载所有 mod

    目录名即 mod_id, 依赖在 info.json 的 dependencies 中声明
    依赖缺失或成环的 mod 会被跳过并记录日志
    """
    if TYPE_CHECKING:
        return
    mods_dir = Path(__file__).resolve().parent / "mods"
    if not mods_dir.is_dir():
        return
    cards.mods_dir = mods_dir
    dirs: dict[str, Path] = {}
    infos: dict[str, ModInfo] = {}
    for mod_dir in sorted(mods_dir.iterdir()):
        if not mod_dir.is_dir() or mod_dir.name.startswith(("_", ".")):
            continue
        mod_id = mod_dir.name
        if mod_id in loaded_mods:
            logger.warning(f"mod 重复, 已跳过: {mod_id}")
            continue
        dirs[mod_id] = mod_dir
        infos[mod_id] = _read_mod_info(mod_dir, mod_id)
    for mod_id in _resolve_load_order(dirs, infos):
        _load_mod(dirs[mod_id], mod_id, infos[mod_id])
        loaded_mods.add(mod_id)
        logger.info(f"已加载 mod: {mod_id}")
    _apply_replacements(dirs)

# ==================== 牌组与开局 ====================


# 默认卡组池, 循环填满 39 张
# 测试配置: 只保留 AT>=4 的单位, 提高抽牌与空军数量
DEFAULT_DECK_NAME: str = "测试卡组"
"""默认卡组名称"""
DEFAULT_DECK_POOL: list[str] = [
    # 开发
    "kards:card_air_land_sea",
    # 选取
    "kards:card_spoils_of_war",
    # 过牌
    "kards:card_section_ii",
    "kards:card_five_year_plan",
    "kards:card_enemy_contact",
    "kards:card_war_bonds",
    # 守护
    "kards:card_15th_motor_rifles",
    "kards:card_royal_west_kents",
    # 本次测试卡
    "kards:card_sd_kfz_10_pak_38",
    "kards:card_type_93",
    "kards:card_isolation",
    "kards:card_40_panzergrenadier",
    "kards:card_289th_gatchina",
    "kards:97th_rifles",
    "kards:card_414th_rifles",
    "kards:card_yokosuka_e14y",
    "kards:card_75th_rifle_regiment",
    "kards:card_kawanishi_h8k",
    "kards:card_44th_silesia",
    "kards:card_909th_roslavl",
    "kards:card_air_corps_ferrying",
    "kards:card_3rd_morskoi_pekhoty",
    "kards:card_178th_guard_rifles",
    "kards:card_55th_rifles",
    "kards:card_ilyushin_il10",
    "kards:card_little_cobra",
    "kards:card_740th_rifle_regiment",
    "kards:card_4th_guards_rifles",
    "kards:card_kv1_1941",
    "kards:card_kv1_1939",
    "kards:card_t3485_1945",
    "kards:card_2nd_west_africa",
    "kards:card_no_46_commando",
    "kards:card_m3a3_honey",
    "kards:card_the_holy_boys",
    "kards:card_hampshire_regiment",
    "kards:card_su100",
    "kards:card_soviet_military_research",
]


DECKS: dict[str, list[str]] = {DEFAULT_DECK_NAME: DEFAULT_DECK_POOL}
"""已命名的卡组, 默认卡组为测试卡组"""
DEFAULT_DECK: str = DEFAULT_DECK_NAME
"""当前默认卡组名"""
DECK_DIR: Path = Path(__file__).resolve().parent / "mods" / "kards" / "data" / "decks"
"""卡组数据目录"""
_decks_loaded: bool = False


def load_decks() -> None:
    """从 mods/kards/data/decks 读取命名卡组。

    卡组文件只保存卡牌 id, 卡牌对象和属性仍由卡牌数据统一创建。
    """
    global _decks_loaded
    if _decks_loaded:
        return
    _decks_loaded = True
    if not DECK_DIR.is_dir():
        return
    for path in sorted(DECK_DIR.glob("*.json")):
        try:
            raw = cast(object, json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            logger.warning("卡组读取失败 %s: %s", path, exc)
            continue
        record = _string_dict(raw)
        name_value = record.get("name", path.stem)
        name = name_value if isinstance(name_value, str) else path.stem
        card_ids = _object_list(record.get("cards"))
        valid = [
            item for item in card_ids
            if isinstance(item, str) and cards.has(item)
        ]
        missing = [
            item for item in card_ids
            if isinstance(item, str) and not cards.has(item)
        ]
        if missing:
            logger.warning("卡组 %s 含未实现卡牌, 已忽略: %s", name, ", ".join(missing))
        if valid:
            DECKS[name] = valid


def default_deck_ids() -> list[str]:
    """返回当前默认卡组的卡牌 id 列表。"""
    load_decks()
    return DECKS.get(DEFAULT_DECK, DEFAULT_DECK_POOL)


MAJOR_COUNTRIES: frozenset[Country] = frozenset(
    {
        Country.SOVIET,
        Country.GERMANY,
        Country.JAPAN,
        Country.USA,
        Country.BRITAIN,
    }
)
"""可以作为主国的国家(UN 按英国处理)"""

ALLY_CARD_LIMIT: int = 12
"""盟国卡牌数量上限"""

RARITY_COPY_LIMITS: dict[str, int] = {
    "elite": 1,
    "special": 2,
    "limited": 3,
    "standard": 4,
}
"""稀有度对应的单卡携带上限(金/银/铜/铁)"""


def deck_country(card: CardData | Card, main: Country, ally: Country) -> Country:
    """
    返回卡牌在卡组构筑中的国家

    流亡卡: 原国家不是主/盟国时, 按流亡目标国家计算

    Args:
        card: 卡牌或卡牌数据
        main: 主国
        ally: 盟国

    Returns:
        构筑国家
    """
    if card.exile_to is not None and card.country not in (main, ally):
        return card.exile_to
    return card.country


def validate_deck(
    card_ids: list[str],
    main: Country,
    ally: Country | None,
    hq_country: Country | None = None,
) -> list[str]:
    """
    校验卡组构筑规则

    Args:
        card_ids: 卡牌 id 列表
        main: 主国
        ally: 盟国
        hq_country: 总部国家

    Returns:
        错误信息列表, 空列表表示合法
    """
    errors: list[str] = []
    if ally is None:
        errors.append("必须选择盟国")
    elif ally == main:
        errors.append("主国与盟国必须不同")
    if main not in MAJOR_COUNTRIES:
        errors.append(f"主国必须是主要国家: {main.name}")
    if main is Country.NEUTRAL:
        errors.append("中立不能作为主国")
    if ally is Country.NEUTRAL:
        errors.append("中立不能作为盟国")
    if hq_country is not None and hq_country is not main:
        errors.append("总部必须为主国")
    ally_count = 0
    counts: dict[str, int] = {}
    for card_id in card_ids:
        counts[card_id] = counts.get(card_id, 0) + 1
        data = cards.get(card_id)
        if data is None:
            errors.append(f"未注册的卡牌: {card_id}")
            continue
        if data.country is Country.NEUTRAL:
            errors.append(f"中立牌不能加入卡组: {data.display_name or data.name}")
            continue
        country = deck_country(data, main, main if ally is None else ally)
        if country not in (main, ally):
            errors.append(f"{data.display_name or data.name} 不属于主国或盟国")
            continue
        if country == ally:
            ally_count += 1
            if str(data.rare) == "elite":
                errors.append(f"盟国不能包含精英卡: {data.display_name or data.name}")
    if ally_count > ALLY_CARD_LIMIT:
        errors.append(f"盟国卡牌数量不能超过 {ALLY_CARD_LIMIT}")
    for card_id, count in counts.items():
        data = cards.get(card_id)
        if data is None:
            continue
        limit = RARITY_COPY_LIMITS.get(str(data.rare))
        if limit is not None and count > limit:
            errors.append(f"{data.display_name or data.name} 最多携带 {limit} 张")
    return errors


def make_deck(pool: list[str], owner: Player, country: Country | None = None) -> Deck:
    """
    按卡牌 id 池循环构造 39 张卡组

    Args:
        pool: 卡牌 id 池
        owner: 卡组所有者
        country: 总部国家

    Returns:
        卡组
    """
    hq = Card(
        type=CardType.HQ,
        cost=0,
        name="HQ",
        country=country or Country.NEUTRAL,
        at=0,
        df=20,
        display_name="总部",
    )
    hq.owner = owner
    hq.controller = owner
    hq.initial_df = 20
    hq.max_df = 20
    deck_cards = [cards.create(pool[i % len(pool)]) for i in range(Deck.SIZE)]
    for card in deck_cards:
        card.owner = owner
        card.controller = owner
        card.add_tag(CardTag.IN_START)
    return Deck(deck_cards, hq)


def create_battle() -> BattleGround:
    """
    创建默认对局, 本地玩家对阵电脑

    Returns:
        战斗全局参数
    """
    config = BattleConfig(
        host_kind=PlayerKind.HUMAN,
        guest_kind=PlayerKind.AI,
        host_country=Country.SOVIET,
        guest_country=Country.BRITAIN,
        host_ally=Country.BRITAIN,
        guest_ally=Country.POLAND,
        host_deck=default_deck_ids(),
        guest_deck=default_deck_ids(),
    )
    deck_a = make_deck(config.host_deck, Player.A, config.host_country)
    deck_b = make_deck(config.guest_deck, Player.B, config.guest_country)
    ground = BattleGround(config, deck_a, deck_b)
    for player in (Player.A, Player.B):
        ground.hqs[player].df = 20
        ground.hqs[player].max_df = 20
        ground.hqs[player].initial_df = 20
    return ground

# ==================== 全局状态 ====================


# 场景标识
SCENE_MENU: str = "menu"
SCENE_START: str = "start"
SCENE_BATTLE: str = "battle"

# 开始界面选项
START_OPTIONS: list[str] = ["乱斗", "赛事", "竞技场", "战区", "战斗代码", "对战模式"]


@dataclass
class Status:
    """
    程序运行状态, 各字段可随时修改

    Attributes:
        running: 是否正在运行
        paused: 是否暂停
        quitting: 是否正在退出
        scene: 当前场景
    """
    running: bool = True
    """是否正在运行"""
    paused: bool = False
    """是否暂停"""
    quitting: bool = False
    """是否正在退出"""
    scene: str = SCENE_MENU
    """当前场景"""


SAVE_DIR: Path = Path(__file__).resolve().parent / "saves"
LAST_SAVE_FILE: Path = SAVE_DIR / "last.txt"
DEFAULT_ADD_DECK_DELAY: int = 300

THANKS_FILE: Path = Path(__file__).resolve().parent / "configs" / "thanks.json"
"""鸣谢配置文件"""


def load_thanks() -> dict[str, Any]:
    """从 configs/thanks.json 读取鸣谢内容。

    Returns:
        鸣谢数据, 文件缺失或损坏时为空字典
    """
    if not THANKS_FILE.is_file():
        return {}
    try:
        raw = cast(object, json.loads(THANKS_FILE.read_text(encoding="utf-8-sig")))
    except (OSError, ValueError) as exc:
        logger.warning("鸣谢读取失败 %s: %s", THANKS_FILE, exc)
        return {}
    return _string_dict(raw)


DEFAULT_THANKS: dict[str, Any] = load_thanks()
"""默认鸣谢内容, 来自 configs/thanks.json"""


@dataclass
class SaveData:
    """
    存档配置

    Attributes:
        name: 存档名
        path: 存档文件路径
        start_time: 存档开始时间
        add_deck_delay: 加入卡组动画延迟, 毫秒
        fps: 帧率上限
        mods: 本次加载的 mod id
        thanks: 鸣谢内容
    """
    name: str
    path: Path
    start_time: str
    add_deck_delay: int = DEFAULT_ADD_DECK_DELAY
    fps: int = 60
    mods: list[str] = field(default_factory=lambda: [""][:0])
    thanks: dict[str, Any] = field(default_factory=lambda: DEFAULT_THANKS)

    def to_json(self) -> dict[str, Any]:
        """转换为存档 JSON"""
        return {
            "start_time": self.start_time,
            "name": self.name,
            "mods": self.mods,
            "延迟": {"加入卡组": self.add_deck_delay},
            "FPS": self.fps,
            "thanks": self.thanks,
        }


class Global:
    """
    全局级别变量控制

    Attributes:
        FPS: 帧率上限
        status: 程序运行状态
        battle_ground: 战斗全局参数, 进入战斗前为 None
        battle_ui: 战斗界面, 进入战斗前为 None
        save_data: 当前存档配置
    """
    FPS: int = 60
    status: Status = Status()
    battle_ground: BattleGround | None = None
    battle_ui: "BattleUI | None" = None
    save_data: SaveData | None = None


def _next_save_name() -> str:
    """返回下一个可用的数字存档名"""
    numbers: list[int] = []
    if SAVE_DIR.is_dir():
        for path in SAVE_DIR.glob("save*.json"):
            suffix = path.stem.removeprefix("save")
            if suffix.isdigit():
                numbers.append(int(suffix))
    return f"save{max(numbers, default=0) + 1}"


def _write_save(data: SaveData) -> None:
    """写入存档"""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    data.path.write_text(
        json.dumps(data.to_json(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    LAST_SAVE_FILE.write_text(data.name, encoding="utf-8")


def load_or_create_save() -> SaveData:
    """
    读取上次存档, 不存在时创建新存档并写入 last.txt

    Returns:
        存档配置
    """
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    name = ""
    if LAST_SAVE_FILE.is_file():
        name = LAST_SAVE_FILE.read_text(encoding="utf-8").strip()
        name = Path(name).stem
    if not name:
        name = _next_save_name()
    path = SAVE_DIR / f"{name}.json"
    raw: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                raw = _string_dict(loaded)
        except (OSError, json.JSONDecodeError):
            logger.warning("存档读取失败, 将重新创建: %s", path)
    start_time = raw.get("start_time")
    if not isinstance(start_time, str) or not start_time:
        start_time = datetime.now().isoformat(timespec="seconds")
    delay = raw.get("延迟")
    add_deck_delay = DEFAULT_ADD_DECK_DELAY
    if isinstance(delay, dict):
        delay_data = _string_dict(delay)
        value = delay_data.get("加入卡组")
        if isinstance(value, int) and value >= 0:
            add_deck_delay = value
    fps = raw.get("FPS")
    if not isinstance(fps, int) or fps <= 0:
        fps = 60
    mods_raw = raw.get("mods")
    mods: list[str] = []
    if isinstance(mods_raw, list):
        for item in _object_list(mods_raw):
            if isinstance(item, str):
                mods.append(item)
    if not mods:
        mods = sorted(cards.mods)
    thanks = load_thanks()
    if not thanks:
        thanks = DEFAULT_THANKS
    data = SaveData(
        name,
        path,
        start_time,
        add_deck_delay,
        fps,
        mods,
        thanks,
    )
    _write_save(data)
    logger.info(
        "存档: %s, mods=%s, 加入卡组延迟 %sms, FPS %s",
        data.name,
        data.mods,
        data.add_deck_delay,
        data.fps,
    )
    return data


# ==================== 场景与菜单 ====================


def _on_start_option(text: str) -> None:
    """
    开始界面选项的点击回调

    Args:
        text: 选项文字
    """
    if text == "对战模式":
        if "kards" not in loaded_mods:
            logger.warning("未加载 kards mod, 无法进入对战")
            show_alert("未找到 kards mod, 无法开始对战\n\n请确认 mods/kards 目录存在且加载成功")
            return
        ground = create_battle()
        ground.start()
        Global.battle_ground = ground
        Global.status.scene = SCENE_BATTLE
        logger.info("进入战斗")
    else:
        logger.info(f"点击了未实现的选项: {text}")
        show_alert(f"“{text}”模式尚未实现\n\n目前仅支持“对战模式”")


def make_start_buttons(screen_width: int, screen_height: int, font: Font) -> ButtonGroup:
    """
    创建开始界面选项按钮组并自动布局

    Args:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
        font: 按钮文字字体

    Returns:
        按钮组
    """
    btn_height = 64
    gap = 24
    group = ButtonGroup()
    for text in START_OPTIONS:
        group.add(
            Button(
                text=text,
                width=320,
                height=btn_height,
                on_click=lambda t=text: _on_start_option(t),
                color=(60, 70, 90),
                hover_color=(80, 100, 130),
                text_color=(255, 255, 255),
                font_size=36,
                font=font,
            )
        )
    total_height = len(group.buttons) * btn_height + (len(group.buttons) - 1) * gap
    start_y = (screen_height - total_height) // 2
    group.layout_vertical(screen_width // 2, start_y, gap=gap)
    return group


def handle_menu_click(
    pos: tuple[int, int],
    start_rect: pygame.Rect,
    card_rect: pygame.Rect,
) -> None:
    """
    处理主菜单场景的点击

    Args:
        pos: 鼠标点击位置
        start_rect: 开始按钮的碰撞矩形
        card_rect: 卡牌按钮的碰撞矩形
    """
    if start_rect.collidepoint(pos):
        Global.status.scene = SCENE_START
        logger.info("进入开始界面")
    elif card_rect.collidepoint(pos):
        show_alert("卡牌界面尚未完成")


def show_alert(message: str) -> None:
    """
    弹出系统提示对话框

    Args:
        message: 提示内容
    """
    import ctypes
    ctypes.windll.user32.MessageBoxW(None, message, "KardsLike 提示", 0x40)


def draw_menu(
    screen: Surface,
    start_button: Surface,
    start_button_hover: Surface,
    card_button: Surface,
    card_button_hover: Surface,
    start_rect: pygame.Rect,
    card_rect: pygame.Rect,
) -> None:
    """
    绘制主菜单场景

    Args:
        screen: 屏幕 Surface
        start_button: 开始按钮图标
        start_button_hover: 开始按钮悬浮图标
        card_button: 卡牌按钮图标
        card_button_hover: 卡牌按钮悬浮图标
        start_rect: 开始按钮位置
        card_rect: 卡牌按钮位置
    """
    screen.fill((0, 0, 0))
    mouse = pygame.mouse.get_pos()
    screen.blit(
        start_button_hover if start_rect.collidepoint(mouse) else start_button,
        start_rect,
    )
    screen.blit(
        card_button_hover if card_rect.collidepoint(mouse) else card_button,
        card_rect,
    )


def draw_start(screen: Surface, background: Surface, button_group: ButtonGroup) -> None:
    """
    绘制开始界面场景

    Args:
        screen: 屏幕 Surface
        background: 背景图
        button_group: 选项按钮组
    """
    screen.blit(background, (0, 0))
    button_group.update()
    button_group.draw(screen)


def setup() -> Surface:
    """
    初始化 pygame 并创建无边框全屏窗口

    Returns:
        创建好的屏幕 Surface
    """
    if sys.platform == "win32":
        # 开启 DPI 感知, 避免系统把画面放大导致模糊
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.display.set_caption("KardsLike")
    logger.info("窗口创建成功, 分辨率 %s", screen.get_size())
    return screen


def load_font(size: int) -> Font:
    """
    加载支持中文的字体, 找不到则退回默认字体

    Args:
        size: 字号

    Returns:
        字体对象
    """
    path: str | None = (
        pygame.font.match_font("microsoftyahei")
        or pygame.font.match_font("simhei")
        or pygame.font.match_font("simsun")
        or None
    )
    if path is not None:
        return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)

_STAT_FONT_PATH: Path = Path(__file__).resolve().parent / "mods" / "kards" / "assets" / "font" / "Roboto-Black.ttf"
_STAT_FONT_CACHE: dict[int, Font] = {}


def load_stat_font(size: int) -> Font:
    """加载 DIY 数值字体 Roboto Black。

    Args:
        size: 字号

    Returns:
        字体对象, 字体缺失时退回普通字体
    """
    cached = _STAT_FONT_CACHE.get(size)
    if cached is not None:
        return cached
    try:
        font = pygame.font.Font(str(_STAT_FONT_PATH), size)
    except (OSError, pygame.error):
        font = load_font(size)
    _STAT_FONT_CACHE[size] = font
    return font


# ==================== 战斗界面 ====================


class AIController:
    """电脑玩家决策器"""

    def step(self, ground: BattleGround) -> None:
        """
        执行一步电脑决策: 能攻击则攻击, 否则移动, 否则出牌, 最后结束回合

        Args:
            ground: 战斗全局参数
        """
        opponent = Player.B
        credits = ground.kredits[opponent].credits
        support = ground.support_lines[opponent]
        logger.debug(
            "AI 决策: 回合 %s, 指挥点 %s, 手牌 %s, 支援 %s/%s, 前线 %s",
            ground.turn_count,
            credits,
            len(ground.hands[opponent].cards),
            len(support.units),
            support.capacity,
            ground.front_line.owner,
        )

        ready = [card for card in support.units if ground.can_act(card)]
        if ground.front_line.owner is opponent:
            ready.extend(card for card in ground.front_line.units if ground.can_act(card))

        targets: list[Card] = list(ground.support_lines[Player.A].units)
        if ground.front_line.owner is Player.A:
            targets.extend(ground.front_line.units)
        targets.append(ground.hqs[Player.A])

        for attacker in ready:
            if credits < attacker.operation_cost:
                continue
            for target in targets:
                if not ground.can_attack(opponent, attacker, target):
                    continue
                if ground.attack_unit(opponent, attacker, target):
                    return

        front = ground.front_line
        if front.owner in (None, opponent) and len(front.units) < front.capacity:
            movers = sorted(
                (card for card in support.units if ground.can_act(card)),
                key=lambda card: card.at,
                reverse=True,
            )
            for card in movers:
                if credits < card.operation_cost:
                    continue
                if ground.move_unit(opponent, card, front):
                    return

        playable = [card for card in ground.hands[opponent].cards if card.cost <= credits]
        for card in playable:
            if card.is_unit and len(support.units) >= support.capacity:
                continue
            # 指向型指令没有合法目标时不要浪费一次使用
            if card.targeted and card.target_valid is not None:
                if not any(
                    card.target_valid(target, opponent, ground)
                    for target in ground.all_targets()
                ):
                    continue
            if ground.use_card(opponent, card, support.hq_index):
                if ground.pending_target is not None:
                    pending = ground.pending_target
                    target = next((item for item in ground.targets if pending.valid(item)), None)
                    if target is None:
                        ground.cancel_target()
                        ground.end_turn()
                        return
                    ground.resolve_target(target)
                return

        ground.end_turn()


class BattleUI:
    """
    战斗界面, 负责布局、绘制与点击交互

    Attributes:
        selected_hand: 已选中的手牌
        selected_unit: 已选中的己方单位
    """

    MAX_SLOTS: int = 5

    SLAM_SETTINGS: dict[str, tuple[int, float]] = {
        "small": (360, 0.035),
        "medium": (480, 0.070),
        "large": (1200, 0.260),
    }
    """拍桌等级对应的(持续时间毫秒, 震动强度相对卡高)"""

    def __init__(self, loader: ImageLoader, assets: Path, font: Font) -> None:
        """
        创建战斗界面

        Args:
            loader: 图片加载器
            assets: mod 的 assets 目录
            font: 默认字体
        """
        self.loader: ImageLoader = loader
        self.assets: Path = assets
        self.raw_face: Surface = loader.load(assets / "cards" / "card_face.png")
        self.raw_back: Surface = loader.load(assets / "cards" / "card_back.png")
        self.raw_hq: Surface = loader.load(assets / "cards" / "hq_placeholder.png")
        self.eye_image: Surface = loader.load(assets / "ui" / "eye.png")
        self.art_index: dict[str, str] = self._load_art_index(assets)
        self.art_cache: dict[str, Surface | None] = {}
        self.font_cache: dict[int, Font] = {}
        self.selected_hand: Card | None = None
        self.selected_unit: Card | None = None
        self.drag_card: Card | None = None
        self.drag_from_hand: bool = False
        self.drag_pos: tuple[int, int] | None = None
        self.drag_origin: pygame.Rect | None = None
        self.hover_target: Card | None = None
        self.hover_rect: pygame.Rect | None = None
        self.frame_rects: dict[int, tuple[Card, pygame.Rect]] = {}
        self.last_rects: dict[int, tuple[Card, pygame.Rect]] = {}
        self.death_marks: list[tuple[str, pygame.Rect, int]] = []
        self.draw_anims: list[tuple[Player, int]] = []
        self.next_draw_anim: int = 0
        self.next_discard_anim: int = 0
        self.notice_surface: Surface | None = None
        self.notice_surface_size: tuple[int, int] = (0, 0)
        self.notice_until: int = 0
        self.notice_start: int = 0
        self._last_message: str = ""
        self.hooked_ground: BattleGround | None = None
        self.deck_rect: pygame.Rect | None = None
        self.deck_rect_b: pygame.Rect | None = None
        self.keyword_icons: dict[str, Surface | None] = {}
        self.icon_entries: list[tuple[Card, pygame.Rect]] = []
        self.shake_until: int = 0
        self.shake_strength: int = 0
        self.showcase: list[tuple[Card, int]] = []
        self.discard_anims: list[tuple[Card, pygame.Rect, int]] = []
        self.remove_anims: list[tuple[Card, pygame.Rect, int]] = []
        self.slam_anims: dict[int, tuple[Card, pygame.Rect | None, int]] = {}
        self.slam_impacted: set[int] = set()
        self.slam_waves: list[tuple[pygame.Rect, int]] = []
        self.hand_reveal: dict[int, int] = {}
        self.unit_reveal: dict[int, int] = {}
        self.spawn_anims: dict[int, int] = {}
        self.next_unit_anim: int = 0
        self.shuffle_anims: dict[Player, int] = {}
        self.move_anims: dict[int, tuple[Card, pygame.Rect, int]] = {}
        self.return_anims: list[tuple[Card, pygame.Rect, int]] = []
        self.deck_add_anims: list[tuple[Card, pygame.Rect, int]] = []
        self.damage_bullets: list[
            tuple[tuple[int, int], tuple[int, int], int]
        ] = []
        self.attack_fx: list[tuple[tuple[int, int], tuple[int, int], int]] = []
        self.choice_move_anims: list[tuple[Card, pygame.Rect, int]] = []
        self.opp_eye_rect: pygame.Rect | None = None
        self.reveal_hover_start: int = 0
        self.reveal_hover_active: bool = False
        self.last_hand_rects: dict[int, pygame.Rect] = {}
        self.order_origins: dict[int, tuple[int, int]] = {}
        self.preview_card: Card | None = None
        self.selection_cards: list[Card] = []
        self.selection_token: int = 0
        self.confirm_rect: pygame.Rect | None = None
        self.choice_rects: list[tuple[pygame.Rect, Card]] = []
        self.choice_start: int = 0
        self.choice_token: int = 0
        self.choose_rects: list[tuple[pygame.Rect, ChooseOption]] = []
        self.choose_start: int = 0
        self.choose_token: int = 0
        self.message: str = ""
        self.order_anims: list[tuple[Surface, pygame.Rect, int]] = []
        self.ai_timer: int = 0
        self.ai_controller: AIController = AIController()
        self.screen_size: tuple[int, int] = (0, 0)
        self.card_h: int = 0
        self.card_w: int = 0
        self.gap: int = 0
        self.opp_hand_h: int = 0
        self.opp_hand_w: int = 0
        self.opp_hand_y: int = 0
        self.opp_line_y: int = 0
        self.front_y: int = 0
        self.own_line_y: int = 0
        self.own_hand_y: int = 0
        self.status_y: int = 0
        self.margin: int = 0
        self.face: Surface = self.raw_face
        self.back_small: Surface = self.raw_back
        self.hq_image: Surface = self.raw_hq
        self.font: Font = font
        self.small_font: Font = font
        self.big_font: Font = font
        surface: Surface = pygame.display.get_surface()
        self._apply_layout(surface.get_size())
        self.end_button: Button = Button(
            text="结束回合",
            width=self.card_w * 6 // 5,
            height=self.card_h // 3,
            on_click=self._end_turn,
            color=(70, 90, 60),
            hover_color=(90, 120, 80),
            font_size=max(20, self.card_h // 7),
            font=load_font(max(20, self.card_h // 7)),
        )
        self._place_end_button()
        self.continue_button: Button = Button(
            text="继续",
            width=self.card_w * 6 // 5,
            height=self.card_h // 3,
            on_click=self._continue_after_match,
            color=(70, 90, 60),
            hover_color=(90, 120, 80),
            font_size=max(20, self.card_h // 7),
            font=load_font(max(20, self.card_h // 7)),
        )

    def _continue_after_match(self) -> None:
        """对局结束后返回开始界面"""
        Global.battle_ground = None
        Global.status.scene = SCENE_START
        self._clear_drag()
        self.message = ""

    def _ensure_hooks(self, ground: BattleGround) -> None:
        """
        为当前战斗注册界面特效钩子

        Args:
            ground: 战斗全局参数
        """
        if self.hooked_ground is ground:
            return
        self.frame_rects.clear()
        self.last_rects.clear()
        self.death_marks.clear()
        self.draw_anims.clear()
        self.discard_anims.clear()
        self.remove_anims.clear()
        self.slam_anims.clear()
        self.slam_impacted.clear()
        self.slam_waves.clear()
        self.hand_reveal.clear()
        self.unit_reveal.clear()
        self.spawn_anims.clear()
        self.shuffle_anims.clear()
        self.move_anims.clear()
        self.return_anims.clear()
        self.deck_add_anims.clear()
        self.damage_bullets.clear()
        self.attack_fx.clear()
        self.choice_move_anims.clear()
        self.opp_eye_rect = None
        self.reveal_hover_active = False
        self.reveal_hover_start = 0
        self.selection_cards.clear()
        self.selection_token = 0
        self.confirm_rect = None
        self.choice_rects.clear()
        self.choice_start = 0
        self.choice_token = 0
        self.choose_rects.clear()
        self.choose_start = 0
        self.choose_token = 0
        self.showcase.clear()
        self.order_anims.clear()
        self.message = ""
        self._last_message = ""
        self.notice_until = 0
        self.notice_start = 0
        self.next_draw_anim = 0
        self.next_discard_anim = 0
        self.next_unit_anim = 0
        ground.add_hook(EventType.DRAW, self._on_draw_event)
        ground.add_hook(EventType.ADD_TO_HAND, self._on_draw_event)
        ground.add_hook(EventType.ENTER, self._on_enter_event)
        ground.add_hook(EventType.USE, self._on_use_event)
        ground.add_hook(EventType.DISCARD, self._on_discard_event)
        ground.add_hook(EventType.LEAVE, self._on_leave_fx)
        ground.add_hook(EventType.SHUFFLE, self._on_shuffle_event)
        ground.add_hook(EventType.MOVE, self._on_move_event)
        ground.add_hook(EventType.RETREAT, self._on_move_event)
        ground.add_hook(EventType.ADD_TO_DECK, self._on_add_deck_event)
        ground.add_hook(EventType.DAMAGED, self._on_damaged_event)
        ground.add_hook(EventType.ATTACK, self._on_attack_event)
        ground.add_hook(EventType.CHOICE_RESOLVED, self._on_choice_resolved)
        self.hooked_ground = ground

    def _on_add_deck_event(self, event: Event, ground: BattleGround) -> None:
        """
        记录卡牌加入卡组的动画

        Args:
            event: ADD_TO_DECK 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        if not isinstance(card, Card):
            return
        record = self.last_hand_rects.get(id(card))
        if record is not None:
            start = record.copy()
        else:
            start = pygame.Rect(0, 0, self.card_w, self.card_h)
            start.center = (self.screen_size[0] // 2, self.screen_size[1] // 2)
        delay = (
            Global.save_data.add_deck_delay
            if Global.save_data is not None
            else DEFAULT_ADD_DECK_DELAY
        )
        self.deck_add_anims.append(
            (card, start, pygame.time.get_ticks() + delay)
        )

    def _on_damaged_event(self, event: Event, ground: BattleGround) -> None:
        """
        记录伤害来源与目标位置, 用于播放短点射子弹

        Args:
            event: DAMAGED 事件
            ground: 战斗全局参数
        """
        source = event.dict.get("source")
        target = event.dict.get("target")
        if not isinstance(source, Card) or not isinstance(target, Card):
            return
        if source is target:
            return

        def position(card: Card) -> tuple[int, int] | None:
            record = self.frame_rects.get(id(card)) or self.last_rects.get(id(card))
            if record is not None:
                return record[1].center
            hand_rect = self.last_hand_rects.get(id(card))
            if hand_rect is not None:
                return hand_rect.center
            return None

        source_pos = position(source)
        target_pos = position(target)
        if source_pos is None or target_pos is None:
            return
        self.damage_bullets.append(
            (source_pos, target_pos, pygame.time.get_ticks())
        )

    def _on_attack_event(self, event: Event, ground: BattleGround) -> None:
        """记录单位攻击, 用于播放枪口闪光和射击轨迹。

        Args:
            event: ATTACK 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        target = event.dict.get("target")
        if not isinstance(card, Card) or not isinstance(target, Card):
            return

        def position(item: Card) -> tuple[int, int] | None:
            record = self.frame_rects.get(id(item))
            if record is not None:
                return record[1].center
            return None

        source_pos = position(card)
        target_pos = position(target)
        if source_pos is None or target_pos is None:
            return
        self.attack_fx.append((source_pos, target_pos, pygame.time.get_ticks()))

    def _draw_attack_fx(self, screen: Surface) -> None:
        """绘制单位攻击的枪口闪光与短促射击轨迹。

        Args:
            screen: 屏幕 Surface
        """
        if not self.attack_fx:
            return
        now = pygame.time.get_ticks()
        alive: list[tuple[tuple[int, int], tuple[int, int], int]] = []
        for source, target, start in self.attack_fx:
            elapsed = now - start
            if elapsed > 260:
                continue
            alive.append((source, target, start))
            flash = max(0.0, 1.0 - elapsed / 180)
            if flash > 0:
                radius = max(3, int(self.card_w * 0.06 * flash))
                pygame.draw.circle(screen, (255, 225, 135), source, radius + 2)
                pygame.draw.circle(screen, (255, 255, 230), source, max(2, radius // 2))
            tracer = max(0.0, 1.0 - elapsed / 220)
            if tracer > 0:
                end = (
                    int(source[0] + (target[0] - source[0]) * (1.0 - tracer * 0.35)),
                    int(source[1] + (target[1] - source[1]) * (1.0 - tracer * 0.35)),
                )
                pygame.draw.line(screen, (255, 190, 100), source, end, 2)
        self.attack_fx = alive

    def _draw_bullets(self, screen: Surface) -> None:
        """
        绘制从伤害来源飞向目标的短点射, 每次三发

        Args:
            screen: 屏幕 Surface
        """
        if not self.damage_bullets:
            return
        now = pygame.time.get_ticks()
        spacing = 90
        flight = 420
        alive: list[tuple[tuple[int, int], tuple[int, int], int]] = []
        for source_pos, target_pos, start in self.damage_bullets:
            if now - start > spacing * 2 + flight:
                continue
            alive.append((source_pos, target_pos, start))
            for index in range(3):
                progress = (now - start - index * spacing) / flight
                if not 0 <= progress <= 1:
                    continue
                x = int(source_pos[0] + (target_pos[0] - source_pos[0]) * progress)
                y = int(source_pos[1] + (target_pos[1] - source_pos[1]) * progress)
                trail_x = int(source_pos[0] + (target_pos[0] - source_pos[0]) * max(0, progress - 0.12))
                trail_y = int(source_pos[1] + (target_pos[1] - source_pos[1]) * max(0, progress - 0.12))
                pygame.draw.line(screen, (255, 180, 60), (trail_x, trail_y), (x, y), 2)
                pygame.draw.circle(screen, (255, 235, 140), (x, y), 4)
            # 枪口闪光
            if now - start <= spacing * 2:
                pygame.draw.circle(screen, (255, 220, 120), source_pos, 6, 2)
        self.damage_bullets = alive

    def _on_choice_resolved(self, event: Event, ground: BattleGround) -> None:
        """
        记录三选一结果, 三张候选卡一起向左退出

        Args:
            event: CHOICE_RESOLVED 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        if not isinstance(card, Card):
            return
        now = pygame.time.get_ticks()
        records = [(item, rect.copy()) for rect, item in self.choice_rects]
        if not records:
            records = [(card, pygame.Rect(0, 0, self.card_w, self.card_h))]
        for item, rect in records:
            self.choice_move_anims.append((item, rect, now))
        self.choice_rects.clear()

    def _draw_choice_move_anims(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制三选一卡牌向左退出的动画

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if not self.choice_move_anims:
            return
        now = pygame.time.get_ticks()
        duration = 360
        alive: list[tuple[Card, pygame.Rect, int]] = []
        for card, start, start_time in self.choice_move_anims:
            elapsed = now - start_time
            if elapsed >= duration:
                continue
            alive.append((card, start, start_time))
            progress = max(0.0, min(1.0, elapsed / duration))
            ease = 1 - (1 - progress) ** 3
            # 全部飞出屏幕左端
            target_x = -start.width - 24
            x = int(start.x + (target_x - start.x) * ease)
            rect = pygame.Rect(x, start.y, start.width, start.height)
            self._blit_card(screen, card, rect)
        self.choice_move_anims = alive

    def _on_move_event(self, event: Event, ground: BattleGround) -> None:
        """
        记录单位移动动画

        Args:
            event: MOVE 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        if not isinstance(card, Card):
            return
        record = self.frame_rects.get(id(card)) or self.last_rects.get(id(card))
        if record is not None:
            self.move_anims[id(card)] = (card, record[1].copy(), pygame.time.get_ticks() + 100)

    def _on_shuffle_event(self, event: Event, ground: BattleGround) -> None:
        """
        记录卡组洗切动画

        Args:
            event: SHUFFLE 事件
            ground: 战斗全局参数
        """
        player = event.dict.get("player")
        if isinstance(player, Player):
            self.shuffle_anims[player] = pygame.time.get_ticks()

    def _on_discard_event(self, event: Event, ground: BattleGround) -> None:
        """
        记录弃牌特效

        Args:
            event: DISCARD 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        player = event.dict.get("player")
        if not isinstance(card, Card):
            return
        rect = self.last_hand_rects.get(id(card))
        if rect is None:
            if player is Player.A:
                rect = pygame.Rect(0, 0, self.card_w, self.card_h)
                rect.center = (self.screen_size[0] // 2, self.own_hand_y + self.card_h // 2)
            else:
                rect = pygame.Rect(0, 0, self.opp_hand_w, self.opp_hand_h)
                rect.center = (
                    self.screen_size[0] // 2,
                    self.opp_hand_y + self.opp_hand_h // 2 + int(self.card_h * 0.25),
                )
        now = pygame.time.get_ticks()
        start = max(now, self.next_discard_anim)
        self.next_discard_anim = start + 260
        self.discard_anims.append((card, rect.copy(), start))

    def _on_leave_fx(self, event: Event, ground: BattleGround) -> None:
        """
        记录移除特效

        Args:
            event: LEAVE 事件
            ground: 战斗全局参数
        """
        way = event.dict.get("way")
        card = event.dict.get("card")
        if not isinstance(card, Card):
            return
        if way is LeaveMethod.RETURN_HAND:
            record = self.frame_rects.get(id(card)) or self.last_rects.get(id(card))
            rect = record[1].copy() if record is not None else pygame.Rect(0, 0, self.card_w, self.card_h)
            self.return_anims.append((card, rect, pygame.time.get_ticks() + 160))
            return
        if way is LeaveMethod.DESTROYED and card.damage_amount <= 0:
            # 非伤害消灭播放与伤害相同的射击动画
            source = event.dict.get("source")
            if isinstance(source, Card) and source is not card:
                self._on_damaged_event(
                    Event(
                        EventType.DAMAGED,
                        target=card,
                        source=source,
                    ),
                    ground,
                )
            return
        if way is not LeaveMethod.REMOVED:
            return
        record = self.frame_rects.get(id(card)) or self.last_rects.get(id(card))
        rect = record[1].copy() if record is not None else pygame.Rect(0, 0, self.card_w, self.card_h)
        self.remove_anims.append((card, rect, pygame.time.get_ticks()))

    def _on_use_event(self, event: Event, ground: BattleGround) -> None:
        """
        使用指令时记录左侧放大展示

        Args:
            event: USE 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        if (
            isinstance(card, Card)
            and card.type is CardType.ORDER
            and not card.has_tag(CardTag.CHOOSE)
        ):
            self.showcase.append((card, pygame.time.get_ticks()))
            rect = self.last_hand_rects.get(id(card))
            if rect is not None:
                self.order_origins[id(card)] = rect.center

    def _draw_showcase(self, screen: Surface, ground: BattleGround) -> None:
        """
        在屏幕左侧绘制放大展示的指令卡

        指向中的指令卡不显示, 避免和指向箭头叠在一起

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if not self.showcase:
            return
        now = pygame.time.get_ticks()
        duration = 1400
        pending = ground.pending_target
        alive: list[tuple[Card, int]] = []
        for card, start in self.showcase:
            progress = (now - start) / duration
            if progress >= 1:
                continue
            if pending is not None and pending.source is card:
                continue
            alive.append((card, start))
            height = int(self.card_h * 1.6)
            width = int(height * 500 / 702)
            art = self._card_art(card)
            image = pygame.transform.smoothscale(art if art is not None else self.face, (width, height))
            appear = min(1.0, progress * 4)
            disappear = min(1.0, (1 - progress) * 4)
            image.set_alpha(int(255 * min(appear, disappear)))
            x = self.margin - int((1 - appear) * 60)
            y = (screen.get_height() - height) // 2
            screen.blit(image, (x, y))
            pygame.draw.rect(screen, (235, 235, 235), (x, y, width, height), 3, border_radius=6)
        self.showcase = alive

    def _on_draw_event(self, event: Event, ground: BattleGround) -> None:
        """
        双方抽牌时记录一次飞牌动画

        Args:
            event: DRAW 事件
            ground: 战斗全局参数
        """
        player = event.dict.get("player")
        if not isinstance(player, Player):
            return
        now = pygame.time.get_ticks()
        start = max(now, self.next_draw_anim)
        self.next_draw_anim = start + 260
        self.draw_anims.append((player, start))
        card = event.dict.get("card")
        if player is Player.A and isinstance(card, Card):
            self.hand_reveal[id(card)] = start + 200

    def _on_enter_event(self, event: Event, ground: BattleGround) -> None:
        """
        单位部署时按拍桌等级触发画面震动

        Args:
            event: ENTER 事件
            ground: 战斗全局参数
        """
        card = event.dict.get("card")
        if not isinstance(card, Card):
            return
        if event.dict.get("method") == EntryMethod.ADD:
            now = pygame.time.get_ticks()
            start = max(now, self.next_unit_anim)
            self.next_unit_anim = start + 220
            self.unit_reveal[id(card)] = start
            self.spawn_anims[id(card)] = start
            return
        if event.dict.get("method") != EntryMethod.DEPLOY:
            return
        level = self._slam_level(card)
        if level is None:
            return
        now = pygame.time.get_ticks()
        if level == "large":
            self.slam_anims[id(card)] = (card, None, now)
            return
        duration, ratio = self.SLAM_SETTINGS[level]
        self.shake_until = now + duration
        minimum = 3 if level == "small" else 4
        self.shake_strength = max(minimum, int(self.card_h * ratio))

    def _slam_level(self, card: Card) -> str | None:
        """
        返回单位的拍桌等级

        标签优先于 AT+DF 阈值, 同时拥有多个标签时使用最高等级

        Args:
            card: 进入战场的单位

        Returns:
            small/medium/large, 不触发时为 None
        """
        total = card.at + card.df
        has_up = card.has_tag(CardTag.SLAM_UP_1) or card.has_tag(CardTag.SLAM_UP_2)
        if total < 8 and not has_up:
            return None
        if total >= 12:
            level = 2
        elif total >= 10:
            level = 1
        else:
            level = 0
        if card.has_tag(CardTag.SLAM_UP_1):
            level += 1
        if card.has_tag(CardTag.SLAM_UP_2):
            level += 2
        level = min(level, 2)
        return ("small", "medium", "large")[level]

    def _apply_layout(self, size: tuple[int, int]) -> None:
        """
        按屏幕分辨率计算相对布局

        Args:
            size: 屏幕宽高
        """
        if size == self.screen_size:
            return
        self.screen_size = size
        width, height = size
        self.card_h = max(80, int(height * 0.195))
        self.card_w = max(56, int(self.card_h * 500 / 702))
        self.gap = max(8, int(self.card_w * 0.20))
        self.opp_hand_h = max(40, int(height * 0.090))
        self.opp_hand_w = max(30, int(self.opp_hand_h * 500 / 702))
        self.opp_hand_y = int(height * 0.004)
        self.opp_line_y = int(height * 0.096)
        self.front_y = int(height * 0.300)
        self.own_line_y = int(height * 0.504)
        self.own_hand_y = int(height * 0.708)
        self.status_y = int(height * 0.900)
        self.margin = max(12, int(width * 0.021))
        self.face = pygame.transform.smoothscale(self.raw_face, (self.card_w, self.card_h))
        self.back_small = pygame.transform.smoothscale(self.raw_back, (self.opp_hand_w, self.opp_hand_h))
        self.deck_back = pygame.transform.smoothscale(self.raw_back, (self.card_w, self.card_h))
        self.hq_image = pygame.transform.smoothscale(self.raw_hq, (self.card_w, self.card_h))
        self.font = load_font(max(20, int(height * 0.030)))
        self.small_font = load_font(max(14, int(height * 0.020)))
        self.big_font = load_font(max(40, int(height * 0.066)))
        self.font_cache = {}
        self.art_cache = {}

    def _place_end_button(self) -> None:
        """把结束回合按钮放到右下角"""
        width, height = self.screen_size
        self.end_button.rect.center = (
            width - self.margin - self.end_button.rect.width // 2,
            self.status_y + int(height * 0.043),
        )

    def _end_turn(self) -> None:
        """结束当前回合并清空选中, 仅己方回合有效"""
        ground = Global.battle_ground
        if ground is not None and ground.pending_choice is not None:
            ground.resolve_random_choice()
        if ground is not None and ground.pending_selection is not None:
            self._auto_select(ground)
        if ground is not None and ground.turn_owner is Player.A:
            ground.end_turn()
        self.selected_hand = None
        self.selected_unit = None

    def _auto_select(self, ground: BattleGround) -> None:
        """
        结束回合时按从左到右自动完成选取

        Args:
            ground: 战斗全局参数
        """
        request = ground.pending_selection
        if request is None or request.player is not Player.A:
            return
        chosen = list(self.selection_cards)
        for card in ground.hands[Player.A].cards:
            if len(chosen) >= request.max_count:
                break
            if card in chosen:
                continue
            if request.filter is not None and not request.filter(card):
                continue
            chosen.append(card)
        if not ground.resolve_selection(chosen):
            ground.cancel_selection()
        self.selection_cards.clear()

    def _add_order_anim(self, rect: pygame.Rect) -> None:
        """记录一次指令脱离手牌的动画"""
        self.order_anims.append((self.face, rect.copy(), pygame.time.get_ticks()))

    def _draw_order_anims(self, screen: Surface) -> None:
        """绘制指令脱离手牌的动画"""
        now = pygame.time.get_ticks()
        alive: list[tuple[Surface, pygame.Rect, int]] = []
        for image, rect, start in self.order_anims:
            progress = (now - start) / 450
            if progress >= 1:
                continue
            flying = image.copy()
            flying.set_alpha(int(255 * (1 - progress)))
            screen.blit(flying, rect.move(0, -int(180 * progress)))
            alive.append((image, rect, start))
        self.order_anims = alive

    def update(self, dt: int) -> None:
        """
        每帧更新, 驱动电脑回合

        Args:
            dt: 距上一帧的毫秒数
        """
        ground = Global.battle_ground
        if ground is None or ground.winner is not None:
            return
        if ground.pending_selection is not None:
            return
        if ground.pending_choice is not None:
            return
        if ground.pending_choose is not None:
            return
        if ground.turn_owner is Player.B and ground.kind_of(Player.B) is PlayerKind.AI:
            self.ai_timer += dt
            if self.ai_timer >= 1000:
                self.ai_timer = 0
                self.ai_controller.step(ground)
        else:
            self.ai_timer = 0

    def _text(
        self,
        screen: Surface,
        text: str,
        pos: tuple[int, int],
        color: Color = (191, 198, 179),
        font: Font | None = None,
        center: bool = False,
    ) -> None:
        """在指定位置绘制文字"""
        surface = (font or self.small_font).render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        screen.blit(surface, rect)

    NATION_DIRS: dict[Country, str] = {
        Country.ANZAC: "Anzac",
        Country.BRITAIN: "Britain",
        Country.FINLAND: "Finland",
        Country.FRANCE: "France",
        Country.GERMANY: "Germany",
        Country.ITALY: "Italy",
        Country.JAPAN: "Japan",
        Country.NEUTRAL: "Neutral",
        Country.POLAND: "Poland",
        Country.SOVIET: "Soviet",
        Country.USA: "USA",
    }

    @staticmethod
    def _load_art_index(assets: Path) -> dict[str, str]:
        """
        读取中文名与卡图的对应索引

        Args:
            assets: 资源根目录

        Returns:
            卡牌 id 与中文名到卡图相对路径的映射
        """
        index_path = assets.parent / "data" / "art_index.json"
        if not index_path.is_file():
            return {}
        try:
            raw: object = json.loads(index_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return {}
        mapping: dict[str, str] = {}
        if not isinstance(raw, dict):
            return mapping
        for card_id, record in _string_dict(raw).items():
            if not isinstance(record, dict):
                continue
            entry = _string_dict(record)
            path = str(entry.get("path", ""))
            if not path:
                continue
            mapping[card_id] = path
            title = str(entry.get("title", ""))
            if title:
                mapping[title] = path
        return mapping

    def display_title(self, card: Card) -> str:
        """
        返回卡牌显示名, 优先中文

        Args:
            card: 卡牌

        Returns:
            显示名
        """
        return card.display_name or card.name

    def _card_art(self, card: Card) -> Surface | None:
        """
        加载卡图, 优先用中文名或 id 查索引, 再退回国家目录

        Args:
            card: 卡牌

        Returns:
            卡图, 不存在时为 None
        """
        key = f"{card.name}:{card.art}"
        if key in self.art_cache:
            return self.art_cache[key]
        art = card.art
        relative = self.art_index.get(card.display_name) or self.art_index.get(card.name)
        path: Path | None = None
        if art:
            nation = self.NATION_DIRS.get(card.country)
            if nation:
                path = self.assets / "cards" / nation / art
        if path is None or not path.is_file():
            if relative:
                path = self.assets / "cards" / relative
        if path is None or not path.is_file():
            nation = self.NATION_DIRS.get(card.country)
            asset_name = card.name.removeprefix("card_")
            path = self.assets / "cards" / nation / f"{asset_name}.png" if nation else None
        image: Surface | None = None
        if path is not None and path.is_file():
            try:
                image = pygame.transform.smoothscale(pygame.image.load(str(path)), (self.card_w, self.card_h))
            except pygame.error:
                image = None
        self.art_cache[key] = image
        return image

    def _blit_card(self, screen: Surface, card: Card, rect: pygame.Rect, show_keywords: bool = False) -> None:
        """
        绘制卡面, 有卡图用卡图并覆盖实际数值, 否则用占位卡面加中文文字

        Args:
            screen: 屏幕 Surface
            card: 卡牌
            rect: 目标矩形
            show_keywords: 是否记录关键词图标(只在场上显示)
        """
        art = self._card_art(card)
        if art is not None:
            if art.get_size() != rect.size:
                art = pygame.transform.smoothscale(art, rect.size)
            screen.blit(art, rect)
            self._draw_stats_overlay(screen, card, rect)
        else:
            screen.blit(self.face, rect)
            self._text(screen, self.display_title(card)[:6], (rect.centerx, rect.y + 12), (25, 25, 25), center=True)
            self._text(screen, str(card.cost), (rect.x + 6, rect.y + 4), (30, 30, 110))
            if card.is_unit:
                self._text(screen, str(card.at), (rect.x + 6, rect.bottom - 26), (20, 90, 30))
                self._text(screen, str(card.df), (rect.right - 26, rect.bottom - 26), (110, 30, 30))
        if show_keywords:
            self.icon_entries.append((card, rect))

    def _keyword_icon(self, keyword_id: str) -> Surface | None:
        """
        加载并缓存关键词图标

        Args:
            keyword_id: 关键词 id

        Returns:
            图标 Surface, 无图标时为 None
        """
        if keyword_id in self.keyword_icons:
            return self.keyword_icons[keyword_id]
        keyword = cards.keywords.get(keyword_id)
        image: Surface | None = None
        if keyword is not None and keyword.icon:
            path = self.assets / "keyword" / keyword.icon
            if path.is_file():
                try:
                    image = pygame.image.load(str(path)).convert_alpha()
                except pygame.error:
                    image = None
        self.keyword_icons[keyword_id] = image
        return image

    def _card_icon_items(
        self, card: Card, ground: BattleGround
    ) -> list[tuple[str, str | int]]:
        """
        汇总一张卡需要显示的全部状态图标

        Args:
            card: 卡牌
            ground: 战斗全局参数

        Returns:
            按从上到下顺序排列的图标描述
        """
        items: list[tuple[str, str | int]] = []
        if card.inhibited:
            items.append(("inhibited", 0))
        for keyword_id in dict.fromkeys([*card.keywords, *card.aura_keywords]):
            if keyword_id == "armor":
                continue
            if keyword_id == "countdown":
                value = card.keyword_values.get("countdown", 0)
                items.append(("countdown", value if isinstance(value, int) else 0))
            elif self._keyword_icon(keyword_id) is not None:
                items.append(("keyword", keyword_id))
        armor = min(max(card.armor, 0), 3)
        if armor > 0:
            items.append(("armor", armor))
        if card.immune:
            items.append(("immune", 0))
        if card.suppressed:
            items.append(("suppressed", 0))
        if ground.is_guarded(card):
            items.append(("guarded", 0))
        return items

    def _draw_card_icons(
        self,
        screen: Surface,
        card: Card,
        rect: pygame.Rect,
        ground: BattleGround,
    ) -> None:
        """
        自动绘制一张卡右侧的全部图标

        Args:
            screen: 屏幕 Surface
            card: 卡牌
            rect: 卡牌矩形
            ground: 战斗全局参数
        """
        self._draw_icon_sequence(screen, rect, self._card_icon_items(card, ground))

    def _draw_icon_sequence(
        self,
        screen: Surface,
        rect: pygame.Rect,
        items: list[tuple[str, str | int]],
    ) -> None:
        """
        按顺序绘制一组状态图标

        Args:
            screen: 屏幕 Surface
            rect: 卡牌矩形
            items: 图标描述列表
        """
        size = max(14, int(rect.width * 0.20))
        gap = max(2, size // 8)
        x = rect.right
        y = rect.y
        for kind, value in items:
            if kind == "inhibited":
                pygame.draw.rect(screen, (70, 25, 25), (x, y, size, size))
                pygame.draw.rect(screen, (220, 60, 60), (x, y, size, size), 2)
                pygame.draw.line(
                    screen,
                    (235, 80, 80),
                    (x + 3, y + 3),
                    (x + size - 3, y + size - 3),
                    3,
                )
                pygame.draw.line(
                    screen,
                    (235, 80, 80),
                    (x + size - 3, y + 3),
                    (x + 3, y + size - 3),
                    3,
                )
                y += size + gap
                continue
            icon_id = str(value) if kind == "keyword" else kind
            if kind == "armor":
                icon = self._keyword_icon("guard")
            elif kind == "countdown":
                icon = self._keyword_icon("countdown")
            else:
                icon = self._keyword_icon(icon_id)
            if icon is None:
                continue
            image = pygame.transform.smoothscale(icon, (size, size))
            screen.blit(image, (x, y))
            pygame.draw.rect(screen, (25, 25, 25), (x, y, size, size), 1)
            if kind in ("armor", "countdown"):
                font_size = max(10, int(size * (0.46 if kind == "countdown" else 0.62)))
                font = self.font_cache.get(font_size)
                if font is None:
                    font = load_font(font_size)
                    self.font_cache[font_size] = font
                text = str(value)
                if kind == "countdown":
                    badge_center = (x + int(size * 0.82), y + int(size * 0.82))
                    pygame.draw.circle(screen, (30, 27, 18), badge_center, max(6, size // 3))
                    pygame.draw.circle(screen, (205, 170, 95), badge_center, max(6, size // 3), 1)
                    number = font.render(text, True, (255, 240, 200))
                    screen.blit(number, number.get_rect(center=badge_center))
                else:
                    shadow = font.render(text, True, (30, 24, 10))
                    number = font.render(text, True, (255, 255, 255))
                    center = (x + size // 2, y + size // 2)
                    for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        screen.blit(
                            shadow,
                            shadow.get_rect(center=(center[0] + offset[0], center[1] + offset[1])),
                        )
                    screen.blit(number, number.get_rect(center=center))
            y += size + gap

    def _draw_all_keyword_icons(self, screen: Surface, ground: BattleGround) -> None:
        """
        在所有卡牌绘制完成后统一绘制状态图标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        for card, rect in self.icon_entries:
            self._draw_card_icons(screen, card, rect, ground)

    def _draw_hq_icons(self, screen: Surface, ground: BattleGround) -> None:
        """
        按与单位一致的方式绘制总部状态图标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        for hq in (ground.hqs[Player.A], ground.hqs[Player.B]):
            record = self.frame_rects.get(id(hq))
            if record is None:
                continue
            items: list[tuple[str, str | int]] = []
            if ground.is_guarded(hq):
                items.append(("guarded", 0))
            if ground.is_immune(hq):
                items.append(("immune", 0))
            self._draw_icon_sequence(screen, record[1], items)

    def _cover(
        self,
        screen: Surface,
        rect: pygame.Rect,
        fx: float,
        fy: float,
        fw: float,
        fh: float,
        color: Color = (58, 61, 54),
    ) -> None:
        """
        按比例用黑色遮住卡面上的一小块区域

        Args:
            screen: 屏幕 Surface
            rect: 卡牌矩形
            fx: 起始横向比例
            fy: 起始纵向比例
            fw: 宽度比例
            fh: 高度比例
        """
        area = pygame.Rect(
            rect.x + int(fx * rect.width),
            rect.y + int(fy * rect.height),
            max(1, int(fw * rect.width)),
            max(1, int(fh * rect.height)),
        )
        pygame.draw.rect(
            screen,
            color,
            area,
            border_radius=max(2, area.width // 10),
        )

    def _draw_value(
        self,
        screen: Surface,
        value: str,
        rect: pygame.Rect,
        fx: float,
        fy: float,
        scale: float,
        color: Color,
    ) -> None:
        """
        在卡牌指定比例位置居中绘制数值

        Args:
            screen: 屏幕 Surface
            value: 数值文本
            rect: 卡牌矩形
            fx: 中心横向比例
            fy: 中心纵向比例
            scale: 字号相对卡牌高度的比例
            color: 文字颜色
        """
        size = max(8, int(rect.height * scale))
        font = load_stat_font(size)
        surface = font.render(value, True, color)
        center = (rect.x + int(fx * rect.width), rect.y + int(fy * rect.height))
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_stats_overlay(self, screen: Surface, card: Card, rect: pygame.Rect) -> None:
        """
        覆盖卡面自带的费用/行动花费/攻击/防御, 并写入当前实际数值

        不信任原卡图上的旧数值, 全部按当前状态重绘。

        Args:
            screen: 屏幕 Surface
            card: 卡牌
            rect: 卡牌矩形
        """
        # 费用: DIY 500x702 坐标 left 17, top 3
        self._cover(screen, rect, 0.015, 0.015, 0.100, 0.115, (49, 51, 46))
        self._draw_value(screen, str(card.cost), rect, 0.079, 0.072, 0.108, (191, 198, 179))
        if not card.is_unit:
            return
        # 行动花费: left 62, top 45
        self._cover(screen, rect, 0.124, 0.064, 0.040, 0.057, (50, 51, 45))
        self._draw_value(
            screen,
            str(card.operation_cost),
            rect,
            0.144,
            0.093,
            0.047,
            (191, 198, 179),
        )
        # 攻击: left 101, top 477
        self._cover(screen, rect, 0.215, 0.680, 0.105, 0.095, (58, 61, 54))
        at_color = (120, 255, 140) if card.at > card.initial_at else (191, 198, 179)
        self._draw_value(screen, str(card.at), rect, 0.258, 0.729, 0.080, at_color)
        # 防御: left 343, top 477
        self._cover(screen, rect, 0.690, 0.680, 0.110, 0.095, (69, 71, 66))
        if card.df < card.max_df:
            df_color = (255, 90, 90)
        elif card.max_df > card.initial_df:
            df_color = (120, 255, 140)
        else:
            df_color = (191, 198, 179)
        self._draw_value(screen, str(card.df), rect, 0.742, 0.729, 0.080, df_color)

    def line_rects(self, screen: Surface, count: int, y: int) -> list[pygame.Rect]:
        """
        返回一条战线上 count 个卡位的矩形, 整体沿屏幕中线对称

        Args:
            screen: 屏幕 Surface
            count: 卡位数量
            y: 战线纵坐标

        Returns:
            卡位矩形列表
        """
        if count <= 0:
            return []
        total = count * self.card_w + (count - 1) * self.gap
        start = (screen.get_width() - total) // 2
        return [
            pygame.Rect(start + i * (self.card_w + self.gap), y, self.card_w, self.card_h)
            for i in range(count)
        ]

    def hand_rects(self, screen: Surface, count: int) -> list[pygame.Rect]:
        """
        返回己方手牌的矩形列表

        Args:
            screen: 屏幕 Surface
            count: 手牌数量

        Returns:
            手牌矩形列表
        """
        panel_size = max(70, int(self.screen_size[1] * 0.078))
        left = self.margin + panel_size + 12
        right = screen.get_width() - self.margin - self.card_w - 12
        available = max(1, right - left)
        gap = self.gap
        if count > 1:
            max_gap = (available - count * self.card_w) // (count - 1)
            gap = min(gap, max_gap)
        if count >= 4:
            # 扇形手牌允许轻微遮挡, 让整组更紧凑
            gap = min(gap, -int(self.card_w * 0.14))
        total = count * self.card_w + max(0, count - 1) * gap
        start = (screen.get_width() - total) // 2
        start = max(self.margin, min(start, screen.get_width() - self.margin - total))
        # 扇形圆心在屏幕下方 (X/2, 3Y/2), 中心卡最高, 两侧沿圆弧向下
        pivot_x = screen.get_width() / 2
        pivot_y = screen.get_height() * 1.5
        base_center_y = self.own_hand_y + self.card_h / 2
        radius = max(1.0, pivot_y - base_center_y)
        result: list[pygame.Rect] = []
        for i in range(count):
            center_x = start + i * (self.card_w + gap) + self.card_w / 2
            dx = center_x - pivot_x
            arc_offset = radius - math.sqrt(max(0.0, radius * radius - dx * dx))
            # 压低弧度, 保持扇形但不要把两侧拉得过低
            center_y = base_center_y + arc_offset * 0.32
            result.append(
                pygame.Rect(
                    int(center_x - self.card_w / 2),
                    int(center_y - self.card_h / 2),
                    self.card_w,
                    self.card_h,
                )
            )
        return result

    def line_items(
        self,
        screen: Surface,
        line: Line,
        y: int,
        exclude: Card | None = None,
        preview_index: int | None = None,
    ) -> tuple[list[tuple[pygame.Rect, Card]], pygame.Rect | None, pygame.Rect | None]:
        """
        计算一条战线上单位与总部的位置

        支援阵线中总部与单位一起参与排列, 整条战线始终沿屏幕中线对称

        Args:
            screen: 屏幕 Surface
            line: 战线
            y: 纵坐标
            exclude: 需要暂时隐藏的单位(拖拽中的单位)
            preview_index: 预览插入位置

        Returns:
            (单位与矩形列表, 总部矩形, 预览空位矩形)
        """
        sequence = self._sequence(line, exclude)
        if preview_index is not None:
            index = max(0, min(preview_index, len(sequence)))
            sequence = sequence[:index] + ["PREVIEW"] + sequence[index:]
        rects = self.line_rects(screen, len(sequence), y)
        pairs: list[tuple[pygame.Rect, Card]] = []
        hq_rect: pygame.Rect | None = None
        preview_rect: pygame.Rect | None = None
        for rect, item in zip(rects, sequence):
            if isinstance(item, str):
                if item == "HQ":
                    hq_rect = rect
                else:
                    preview_rect = rect
            else:
                pairs.append((rect, item))
        return pairs, hq_rect, preview_rect

    def _sequence(self, line: Line, exclude: Card | None = None) -> list[Card | str]:
        """
        返回战线上的卡位顺序, "HQ" 表示总部位置

        Args:
            line: 战线
            exclude: 需要暂时隐藏的单位

        Returns:
            卡位顺序列表
        """
        units = [card for card in line.units if card is not exclude]
        if line.kind is not LineKind.SUPPORT:
            return list(units)
        hq_index = line.hq_index
        if exclude is not None and exclude in line.units and line.units.index(exclude) < hq_index:
            hq_index -= 1
        sequence: list[Card | str] = []
        for index, unit in enumerate(units):
            if index == hq_index:
                sequence.append("HQ")
            sequence.append(unit)
        if hq_index >= len(units):
            sequence.append("HQ")
        return sequence

    def hq_rect(self, screen: Surface, line: Line, y: int) -> pygame.Rect:
        """
        返回总部显示矩形

        Args:
            screen: 屏幕 Surface
            line: 所属支援阵线
            y: 纵坐标

        Returns:
            总部矩形
        """
        _, hq, _ = self.line_items(screen, line, y)
        return hq if hq is not None else pygame.Rect(0, 0, self.card_w, self.card_h)

    def line_units(self, screen: Surface, line: Line, y: int) -> list[tuple[pygame.Rect, Card]]:
        """
        返回战线上单位与矩形的一一对应

        Args:
            screen: 屏幕 Surface
            line: 战线
            y: 纵坐标

        Returns:
            (矩形, 单位) 列表
        """
        pairs, _, _ = self.line_items(screen, line, y)
        return pairs

    def draw(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制战斗界面

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        self._apply_layout(screen.get_size())
        self._place_end_button()
        screen.fill((18, 22, 20))
        self.frame_rects = {}
        self.icon_entries = []
        self._ensure_hooks(ground)
        request = ground.pending_selection
        if request is not None and request.title:
            now = pygame.time.get_ticks()
            self.message = request.title
            self.notice_start = now - 250
            self.notice_until = now + 1000
        self._draw_front_marker(screen, ground)
        preview_line, preview_index = self._preview_target(screen, ground)
        dragging_unit = None if self.drag_from_hand else self.drag_card
        self._draw_opponent_hand(screen, ground)
        self._draw_line(screen, ground, ground.support_lines[Player.B], self.opp_line_y)
        self._draw_line(
            screen,
            ground,
            ground.front_line,
            self.front_y,
            preview_index if preview_line is ground.front_line else None,
            dragging_unit
            if (
                dragging_unit is not None
                and preview_line is ground.front_line
                and preview_index is not None
                and dragging_unit.line is ground.front_line
            )
            else None,
        )
        self._draw_line(
            screen,
            ground,
            ground.support_lines[Player.A],
            self.own_line_y,
            preview_index if preview_line is ground.support_lines[Player.A] else None,
            dragging_unit
            if (
                dragging_unit is not None
                and preview_line is ground.support_lines[Player.A]
                and preview_index is not None
                and dragging_unit.line is ground.support_lines[Player.A]
            )
            else None,
        )
        self._draw_hq(screen, ground, preview_line, preview_index, dragging_unit)
        self._draw_own_hand(screen, ground)
        self._draw_choice_move_anims(screen, ground)
        self._draw_revealed_hover(screen, ground)
        self._draw_all_keyword_icons(screen, ground)
        self._draw_hq_icons(screen, ground)
        self._draw_opponent_eyes(screen)
        self._draw_spawn_anims(screen)
        self._draw_move_anims(screen)
        self._draw_slam_anims(screen)
        self._draw_slam_waves(screen)
        self._draw_order_anims(screen)
        self._draw_drag(screen, ground)
        self._draw_drag_ghost(screen)
        self._draw_target_arrow(screen, ground)
        self._draw_preview_target(screen, ground)
        if self.hover_rect is not None:
            pygame.draw.rect(screen, (235, 70, 70), self.hover_rect, 3, border_radius=4)
        self._update_death_marks()
        self._draw_death_marks(screen)
        self._draw_deck_add_anims(screen, ground)
        self._draw_bullets(screen)
        self._draw_attack_fx(screen)
        self._draw_decks(screen, ground)
        self._draw_draw_anims(screen, ground)
        self._draw_return_anims(screen, ground)
        self._draw_discard_anims(screen)
        self._draw_remove_anims(screen)
        self._draw_showcase(screen, ground)
        self._draw_status(screen, ground)
        self._draw_selection(screen, ground)
        self._draw_choose(screen, ground)
        self._draw_choice(screen, ground)
        if ground.winner is not None:
            self._draw_winner(screen, ground)
        self._apply_shake(screen)

    def _apply_shake(self, screen: Surface) -> None:
        """
        按拍桌等级让整个画面抖动

        Args:
            screen: 屏幕 Surface
        """
        now = pygame.time.get_ticks()
        if now >= self.shake_until:
            return
        snapshot = screen.copy()
        offset_x = random.randint(-self.shake_strength, self.shake_strength)
        offset_y = random.randint(-self.shake_strength, self.shake_strength)
        screen.blit(snapshot, (offset_x, offset_y))

    def _draw_opponent_hand(self, screen: Surface, ground: BattleGround) -> None:
        """绘制对手手牌卡背与明牌眼睛"""
        self.opp_eye_rect = None
        cards = ground.hands[Player.B].cards
        count = len(cards)
        gap = max(3, int(self.opp_hand_w * 0.09))
        total = count * self.opp_hand_w + max(0, count - 1) * gap
        start = (screen.get_width() - total) // 2
        for i in range(count):
            rect = pygame.Rect(
                start + i * (self.opp_hand_w + gap),
                self.opp_hand_y,
                self.opp_hand_w,
                self.opp_hand_h,
            )
            screen.blit(self.back_small, rect)
        if any(card.revealed for card in cards):
            side = max(24, int(self.opp_hand_w * 0.62))
            self.opp_eye_rect = pygame.Rect(
                screen.get_width() // 2 - side // 2,
                self.opp_hand_y + self.opp_hand_h - side + 2,
                side,
                side,
            )

    def _draw_opponent_eyes(self, screen: Surface) -> None:
        """
        在所有卡牌之上绘制对手明牌按钮

        Args:
            screen: 屏幕 Surface
        """
        eye_rect = self.opp_eye_rect
        if eye_rect is None:
            return
        side = eye_rect.width
        padding = 4
        size = side - padding * 2
        eye_image = pygame.transform.smoothscale(self.eye_image, (size, size))
        button = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(button, (0, 0, 0, 190), (side // 2, side // 2), side // 2)
        pygame.draw.circle(button, (235, 235, 235), (side // 2, side // 2), side // 2, 2)
        button.blit(eye_image, (padding, padding))
        screen.blit(button, eye_rect)

    def _draw_selection_stamp(self, screen: Surface, rect: pygame.Rect) -> None:
        """
        在选中的手牌中央绘制红色印章

        Args:
            screen: 屏幕 Surface
            rect: 卡牌矩形
        """
        size = max(30, int(rect.height * 0.42))
        stamp = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(stamp, (215, 45, 45, 70), (size // 2, size // 2), size // 2)
        pygame.draw.circle(stamp, (225, 55, 55, 230), (size // 2, size // 2), size // 2, 4)
        pygame.draw.circle(stamp, (225, 55, 55, 180), (size // 2, size // 2), size // 2 - 10, 2)
        font = self.font_cache.get(size // 2)
        if font is None:
            font = load_font(size // 2)
            self.font_cache[size // 2] = font
        text = font.render("取", True, (235, 60, 60))
        stamp.blit(text, text.get_rect(center=(size // 2, size // 2)))
        screen.blit(stamp, stamp.get_rect(center=rect.center))

    def _draw_selection(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制手牌选取的确认按钮与提示

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        request = ground.pending_selection
        if request is None or request.player is not Player.A:
            self.confirm_rect = None
            self.selection_cards.clear()
            return
        if self.selection_token != id(request):
            self.selection_token = id(request)
            self.selection_cards.clear()
        hand = ground.hands[Player.A].cards
        self.selection_cards = [card for card in self.selection_cards if card in hand]
        count = len(self.selection_cards)
        enabled = request.min_count <= count <= request.max_count
        width, _ = screen.get_size()
        rect = pygame.Rect(width // 2 - 100, self.own_hand_y - 52, 200, 44)
        color = (225, 140, 40) if enabled else (110, 80, 50)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 200, 120), rect, 2, border_radius=8)
        title = request.title or "选取手牌"
        self._text(screen, title, (width // 2, rect.y - 24), (245, 235, 200), center=True)
        self._text(screen, "确定选取", rect.center, (255, 245, 225), center=True)
        self.confirm_rect = rect

    def _draw_revealed_hover(self, screen: Surface, ground: BattleGround) -> None:
        """
        鼠标悬停在对手明牌眼睛上时显示所有明牌

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        eye_rect = self.opp_eye_rect
        if eye_rect is None or not eye_rect.collidepoint(pygame.mouse.get_pos()):
            self.reveal_hover_active = False
            return
        revealed = [card for card in ground.hands[Player.B].cards if card.revealed]
        if not revealed:
            return
        now = pygame.time.get_ticks()
        if not self.reveal_hover_active:
            self.reveal_hover_active = True
            self.reveal_hover_start = now
        progress = min(1.0, (now - self.reveal_hover_start) / 220)
        ease = 1 - (1 - progress) ** 3
        height = int(self.card_h * (0.86 + 0.14 * ease))
        width = max(1, int(height * self.card_w / self.card_h))
        gap = 8
        total = len(revealed) * width + (len(revealed) - 1) * gap
        max_width = screen.get_width() - 2 * self.margin
        if total > max_width:
            height = int(height * max_width / total)
            width = max(1, int(height * self.card_w / self.card_h))
            total = len(revealed) * width + (len(revealed) - 1) * gap
        x = (screen.get_width() - total) // 2
        y = eye_rect.bottom + 8 + int((1 - ease) * 28)
        for card in revealed:
            art = self._card_art(card)
            image = art if art is not None else self.face
            scaled = pygame.transform.smoothscale(image, (width, height))
            rect = pygame.Rect(x, y, width, height)
            screen.blit(scaled, rect)
            self._draw_stats_overlay(screen, card, rect)
            pygame.draw.rect(screen, (235, 235, 235), rect, 2, border_radius=4)
            x += width + gap

    def _draw_choose(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制抉择: 来源卡牌飞到屏幕中间并分成左右两个选项

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        request = ground.pending_choose
        if request is None:
            self.choose_rects.clear()
            return
        now = pygame.time.get_ticks()
        if self.choose_token != id(request):
            self.choose_token = id(request)
            self.choose_start = now
        progress = max(0.0, min(1.0, (now - self.choose_start) / 360))
        ease = 1 - (1 - progress) ** 3
        width = int(self.card_w * 1.12)
        height = int(self.card_h * 1.12)
        gap = max(16, width // 8)
        center_y = screen.get_height() // 2
        origin = self.last_hand_rects.get(id(request.source))
        if origin is None:
            origin = pygame.Rect(0, 0, self.card_w, self.card_h)
            origin.center = (screen.get_width() // 2, center_y)
        start_center = origin.center
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 8, 6, 80))
        screen.blit(overlay, (0, 0))
        self.choose_rects = []
        for index, option in enumerate(request.options[:2]):
            target_x = screen.get_width() // 2 + (index * 2 - 1) * (width + gap) // 2
            target_center = (target_x, center_y)
            current_center = (
                int(start_center[0] + (target_center[0] - start_center[0]) * ease),
                int(start_center[1] + (target_center[1] - start_center[1]) * ease),
            )
            current_w = int(origin.width + (width - origin.width) * ease)
            current_h = int(origin.height + (height - origin.height) * ease)
            rect = pygame.Rect(0, 0, max(1, current_w), max(1, current_h))
            rect.center = current_center
            self._blit_card(screen, option.card, rect)
            pygame.draw.rect(screen, (235, 220, 175), rect, 2, border_radius=4)
            if progress >= 1:
                self.choose_rects.append((rect.copy(), option))

    def _draw_choice(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制三选一界面, 卡牌从右侧进入

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        choice = ground.pending_choice
        if choice is None:
            self.choice_rects.clear()
            return
        now = pygame.time.get_ticks()
        if self.choice_token != id(choice):
            self.choice_token = id(choice)
            self.choice_start = now
        self._text(
            screen,
            choice.title,
            (screen.get_width() // 2, int(screen.get_height() * 0.08)),
            (245, 235, 200),
            center=True,
        )
        width = int(self.card_w * 1.15)
        height = int(self.card_h * 1.15)
        gap = int(width * 0.12)
        center_x = screen.get_width() // 2
        y = (screen.get_height() - height) // 2
        self.choice_rects = []
        for index, card in enumerate(choice.cards):
            delay = index * 80
            progress = max(0.0, min(1.0, (now - self.choice_start - delay) / 320))
            ease = 1 - (1 - progress) ** 3
            x = center_x + (index - 1) * (width + gap) - width // 2
            final = pygame.Rect(x, y, width, height)
            start_x = screen.get_width() + width + index * 40
            draw_x = int(start_x + (final.x - start_x) * ease)
            rect = pygame.Rect(draw_x, y, width, height)
            self._blit_card(screen, card, rect)
            if progress >= 1:
                self.choice_rects.append((final, card))

    def _draw_choice_text(self, screen: Surface, card: Card, rect: pygame.Rect) -> None:
        """
        在三选一卡牌下方显示实际效果文本

        Args:
            screen: 屏幕 Surface
            card: 候选卡牌
            rect: 卡牌矩形
        """
        if card.sub_type != "weather":
            return
        font_size = max(12, rect.width // 14)
        font = load_font(font_size)
        lines = textwrap.wrap(card.text, width=16)[:4]
        if not lines:
            return
        line_height = font.get_linesize()
        panel_h = line_height * len(lines) + 8
        panel = pygame.Rect(rect.x, rect.bottom + 4, rect.width, panel_h)
        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((15, 15, 15, 205))
        screen.blit(overlay, panel)
        for index, line in enumerate(lines):
            image = font.render(line, True, (245, 235, 200))
            screen.blit(
                image,
                image.get_rect(
                    center=(panel.centerx, panel.y + 4 + index * line_height + line_height // 2)
                ),
            )

    def _target_predicate(
        self, ground: BattleGround
    ) -> Callable[[Card], bool] | None:
        """
        返回当前指向状态的目标判定函数

        Args:
            ground: 战斗全局参数

        Returns:
            判定函数, 非指向状态时为 None
        """
        preview = self.preview_card
        if preview is not None:
            validator = preview.target_valid
            if validator is not None:
                return lambda target: validator(target, Player.A, ground)
        if self.drag_card is not None and not self.drag_from_hand and self.drag_card.is_unit:
            attacker = self.drag_card
            return lambda target: ground.can_attack(Player.A, attacker, target)
        if ground.pending_target is not None:
            return ground.pending_target.valid
        return None

    def _draw_line(
        self,
        screen: Surface,
        ground: BattleGround,
        line: Line,
        y: int,
        preview_index: int | None = None,
        exclude: Card | None = None,
    ) -> None:
        """
        绘制一条战线

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
            line: 战线
            y: 纵坐标
            preview_index: 拖拽预览的插入位置
            exclude: 拖拽中需要暂时隐藏的单位
        """
        pairs, _, preview = self.line_items(screen, line, y, exclude=exclude, preview_index=preview_index)
        predicate = self._target_predicate(ground)
        for rect, card in pairs:
            dim = predicate is not None and not predicate(card)
            self._draw_unit(screen, card, rect, dim)
        if preview is not None:
            glow = pygame.Surface(preview.size, pygame.SRCALPHA)
            glow.fill((225, 70, 70, 50))
            screen.blit(glow, preview)
            pygame.draw.rect(screen, (225, 70, 70), preview, 3, border_radius=8)
        if line is ground.front_line:
            pass

    def _draw_spawn_anims(self, screen: Surface) -> None:
        """
        绘制加入战场单位的缩放淡入动画

        Args:
            screen: 屏幕 Surface
        """
        if not self.spawn_anims:
            return
        now = pygame.time.get_ticks()
        duration = 480
        alive: dict[int, int] = {}
        for key, start in self.spawn_anims.items():
            record = self.frame_rects.get(key)
            if record is None:
                alive[key] = start
                continue
            elapsed = now - start
            if elapsed >= duration:
                continue
            alive[key] = start
            progress = max(0.0, min(1.0, elapsed / duration))
            ease = 1 - (1 - progress) ** 3
            card, rect = record
            art = self._card_art(card)
            image = art if art is not None else self.face
            width = max(1, int(rect.width * (0.82 + 0.18 * ease)))
            height = max(1, int(rect.height * (0.82 + 0.18 * ease)))
            scaled = pygame.transform.smoothscale(image, (width, height))
            start_x = screen.get_width() + width
            x = start_x + (rect.centerx - start_x) * ease
            y = rect.centery + int((1 - ease) * 18)
            target = scaled.get_rect(center=(int(x), y))
            screen.blit(scaled, target)
            pygame.draw.rect(screen, (255, 220, 120), target, 2, border_radius=4)
        self.spawn_anims = alive

    def _draw_unit(self, screen: Surface, card: Card, rect: pygame.Rect, dim: bool) -> None:
        """绘制战场上的单位"""
        self.frame_rects[id(card)] = (card, rect)
        now = pygame.time.get_ticks()
        reveal = self.unit_reveal.get(id(card))
        if reveal is not None:
            if now < reveal:
                return
            self.unit_reveal.pop(id(card), None)
        spawn_start = self.spawn_anims.get(id(card))
        if spawn_start is not None:
            if now - spawn_start < 480:
                return
            self.spawn_anims.pop(id(card), None)
        if id(card) in self.slam_anims:
            return
        if id(card) in self.move_anims:
            return
        self._blit_card(screen, card, rect, show_keywords=True)
        border = (90, 90, 90) if dim else (235, 235, 235)
        pygame.draw.rect(screen, border, rect, 2, border_radius=4)
        if dim:
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, rect)
        self._draw_damage(screen, card, rect)
        self._draw_hit_flash(screen, card, rect)
        self._draw_buff(screen, card, rect)

    def _update_death_marks(self) -> None:
        """把本帧消失且带伤害的单位记录为浮动伤害"""
        now = pygame.time.get_ticks()
        for key, (target, rect) in self.last_rects.items():
            if key in self.frame_rects:
                continue
            if target.zone is not Zone.DISCARD:
                continue
            if target.is_unit:
                self.death_marks.append(
                    (str(target.damage_amount) if target.damage_amount > 0 else "消灭", rect.copy(), now)
                )
        self.last_rects = dict(self.frame_rects)

    def _draw_death_marks(self, screen: Surface) -> None:
        """
        在已消失单位的位置绘制骷髅头特效, 持续 2 秒并淡出

        Args:
            screen: 屏幕 Surface
        """
        now = pygame.time.get_ticks()
        alive: list[tuple[str, pygame.Rect, int]] = []
        for text, rect, start in self.death_marks:
            elapsed = now - start
            if elapsed > 2000:
                continue
            alpha = max(0, 255 - int(255 * elapsed / 2000))
            size = max(24, int(rect.height * 0.55))
            self._draw_skull(screen, rect.center, size, alpha)
            alive.append((text, rect, start))
        self.death_marks = alive

    def _draw_skull(self, screen: Surface, center: tuple[int, int], size: int, alpha: int) -> None:
        """
        绘制骷髅头

        Args:
            screen: 屏幕 Surface
            center: 中心位置
            size: 尺寸
            alpha: 透明度
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        width = size
        bone = (235, 235, 235, alpha)
        dark = (25, 25, 25, alpha)
        pygame.draw.ellipse(
            surface, bone, (int(width * 0.12), int(width * 0.06), int(width * 0.76), int(width * 0.62))
        )
        pygame.draw.rect(
            surface,
            bone,
            (int(width * 0.30), int(width * 0.55), int(width * 0.40), int(width * 0.28)),
            border_radius=max(2, int(width * 0.05)),
        )
        eye = max(4, int(width * 0.10))
        pygame.draw.circle(surface, dark, (int(width * 0.35), int(width * 0.30)), eye)
        pygame.draw.circle(surface, dark, (int(width * 0.65), int(width * 0.30)), eye)
        pygame.draw.polygon(
            surface,
            dark,
            [
                (int(width * 0.50), int(width * 0.40)),
                (int(width * 0.44), int(width * 0.52)),
                (int(width * 0.56), int(width * 0.52)),
            ],
        )
        for index in range(3):
            pygame.draw.rect(
                surface,
                dark,
                (
                    int(width * (0.36 + index * 0.10)),
                    int(width * 0.62),
                    max(2, int(width * 0.06)),
                    max(3, int(width * 0.14)),
                ),
            )
        screen.blit(surface, surface.get_rect(center=center))

    def _damage_color(self, kind: DamageType) -> tuple[int, int, int]:
        """
        按伤害类型返回显示颜色

        Args:
            kind: 伤害类型

        Returns:
            RGB 颜色
        """
        if kind is DamageType.BATTLE:
            return (255, 150, 60)
        if kind is DamageType.OTHER:
            return (190, 120, 255)
        return (255, 70, 70)

    def _draw_damage(self, screen: Surface, target: Card, rect: pygame.Rect) -> None:
        """
        单位受伤后 2 秒内在上方显示伤害量

        Args:
            screen: 屏幕 Surface
            target: 受伤对象
            rect: 卡牌矩形
        """
        if target.damage_amount <= 0 or pygame.time.get_ticks() - target.damage_time > 2000:
            return
        size = max(20, int(rect.height * 0.20))
        font = self.font_cache.get(size)
        if font is None:
            font = load_font(size)
            self.font_cache[size] = font
        text = str(target.damage_amount)
        shadow = font.render(text, True, (20, 20, 20))
        surface = font.render(text, True, self._damage_color(target.last_damage_type))
        center = rect.center
        for offset in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            screen.blit(shadow, shadow.get_rect(center=(center[0] + offset[0], center[1] + offset[1])))
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_hit_flash(self, screen: Surface, target: Card, rect: pygame.Rect) -> None:
        """
        单位受到伤害但未死亡时播放短促红色受击闪光

        Args:
            screen: 屏幕 Surface
            target: 受伤单位
            rect: 卡牌矩形
        """
        if not target.is_unit or target.damage_time <= 0:
            return
        if pygame.time.get_ticks() - target.damage_time > 280:
            return
        flash = pygame.Surface(rect.size, pygame.SRCALPHA)
        flash.fill((245, 45, 45, 70))
        screen.blit(flash, rect)
        pygame.draw.rect(screen, (255, 80, 80), rect, 3, border_radius=4)

    def _draw_buff(self, screen: Surface, target: Card, rect: pygame.Rect) -> None:
        """
        属性增加后 2 秒内分别在 AT/DF 位置显示绿色增量

        Args:
            screen: 屏幕 Surface
            target: 增益对象
            rect: 卡牌矩形
        """
        if target.buff_time <= 0 or pygame.time.get_ticks() - target.buff_time > 2000:
            return
        if target.is_hq:
            if target.buff_df:
                self._draw_buff_text(screen, str(target.buff_df), rect, 0.500, 0.680)
            return
        if target.buff_at:
            self._draw_buff_text(screen, str(target.buff_at), rect, 0.267, 0.640)
        if target.buff_df:
            self._draw_buff_text(screen, str(target.buff_df), rect, 0.745, 0.640)

    def _draw_buff_text(
        self,
        screen: Surface,
        text: str,
        rect: pygame.Rect,
        fx: float,
        fy: float,
    ) -> None:
        """
        在卡牌指定比例位置绘制绿色增益文字

        Args:
            screen: 屏幕 Surface
            text: 文字
            rect: 卡牌矩形
            fx: 横向比例
            fy: 纵向比例
        """
        size = max(16, int(rect.height * 0.12))
        font = self.font_cache.get(size)
        if font is None:
            font = load_font(size)
            self.font_cache[size] = font
        shadow = font.render(text, True, (20, 40, 20))
        surface = font.render(text, True, (120, 255, 140))
        center = (int(rect.x + rect.width * fx), int(rect.y + rect.height * fy))
        for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            screen.blit(shadow, shadow.get_rect(center=(center[0] + offset[0], center[1] + offset[1])))
        screen.blit(surface, surface.get_rect(center=center))

    def _draw_hq(
        self,
        screen: Surface,
        ground: BattleGround,
        preview_line: Line | None = None,
        preview_index: int | None = None,
        dragging: Card | None = None,
    ) -> None:
        """
        绘制双方总部与防御力, 并在回合所有者处绘制指示图标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
            preview_line: 拖拽预览所在战线
            preview_index: 拖拽预览插入位置
            dragging: 拖拽中的单位
        """
        for player, line, y in (
            (Player.B, ground.support_lines[Player.B], self.opp_line_y),
            (Player.A, ground.support_lines[Player.A], self.own_line_y),
        ):
            use_preview = preview_index if line is preview_line else None
            exclude = (
                dragging
                if (dragging is not None and use_preview is not None and dragging.line is line)
                else None
            )
            _, hq_rect, _ = self.line_items(screen, line, y, exclude=exclude, preview_index=use_preview)
            if hq_rect is None:
                continue
            rect = hq_rect
            hq = ground.hqs[player]
            self.frame_rects[id(hq)] = (hq, rect)
            screen.blit(self.hq_image, rect)
            pygame.draw.rect(screen, (210, 210, 210), rect, 2, border_radius=4)
            if pygame.time.get_ticks() - hq.damage_time < 280:
                flash = pygame.Surface(rect.size, pygame.SRCALPHA)
                flash.fill((245, 45, 45, 70))
                screen.blit(flash, rect)
                pygame.draw.rect(screen, (255, 80, 80), rect, 3, border_radius=4)
            if hq.df < hq.max_df:
                df_color = (255, 90, 90)
            elif hq.max_df > hq.initial_df:
                df_color = (120, 255, 140)
            else:
                df_color = (240, 240, 240)
            self._text(
                screen, f"DF {hq.df}", (rect.centerx, rect.centery + int(rect.height * 0.27)), df_color, center=True
            )
            self._text(
                screen,
                "我方" if player is Player.A else "对手",
                (rect.centerx, rect.y + int(rect.height * 0.07)),
                (215, 215, 215),
                center=True,
            )
            self._draw_damage(screen, hq, rect)
            self._draw_buff(screen, hq, rect)
            predicate = self._target_predicate(ground)
            if predicate is not None and not predicate(hq):
                overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, rect)

    def _draw_front_marker(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制前线所有者标记: 黑色直线加向下三角波纹

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        line = ground.front_line
        if line.owner is None:
            y = self.front_y + self.card_h // 2
        elif line.owner is Player.B:
            y = (self.own_line_y + self.front_y + self.card_h) // 2
        else:
            y = (self.opp_line_y + self.card_h + self.front_y) // 2
        width = max(3, self.card_h // 60)
        pygame.draw.line(screen, (0, 0, 0), (0, y), (screen.get_width(), y), width)
        size = max(6, self.card_h // 14)
        step = size * 2
        for x in range(0, screen.get_width(), step):
            if line.owner is Player.A:
                points = [(x, y), (x + step, y), (x + step // 2, y - size)]
            else:
                points = [(x, y), (x + step, y), (x + step // 2, y + size)]
            pygame.draw.polygon(screen, (0, 0, 0), points)

    def _draw_turn_icon(self, screen: Surface, ground: BattleGround) -> None:
        """
        在回合所有者所在行的左侧绘制固定位置的回合指示图标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        player = ground.turn_owner
        y = (self.own_line_y if player is Player.A else self.opp_line_y) + self.card_h // 2
        color = (255, 214, 90)
        size = max(10, self.card_h // 14)
        x = self.margin
        pygame.draw.polygon(screen, color, [(x, y - size), (x + size * 3 // 2, y), (x, y + size)])
        pygame.draw.polygon(
            screen,
            (30, 30, 30),
            [(x + size // 4, y - size * 2 // 3), (x + size, y), (x + size // 4, y + size * 2 // 3)],
        )
        self._text(screen, "当前回合", (x, y - size * 2), color)

    def _draw_kredits(
        self, screen: Surface, ground: BattleGround, player: Player, x: int, y: int, label: str
    ) -> None:
        """
        绘制一方的指挥点与槽

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
            player: 所属玩家
            x: 横坐标
            y: 纵坐标
            label: 前缀文字
        """
        kredit = ground.kredits[player]
        color = (240, 210, 90) if player is Player.A else (200, 190, 150)
        size = max(70, int(self.screen_size[1] * 0.078))
        y = min(y, self.screen_size[1] - size - 6)
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, (35, 35, 38), rect, border_radius=6)
        pygame.draw.rect(screen, (150, 150, 150), rect, 2, border_radius=6)
        small = self.small_font
        orange = (240, 150, 60)
        gray = (170, 170, 170)
        label_surface = small.render(label, True, color)
        screen.blit(label_surface, (rect.x + 6, rect.y + 3))
        credit_surface = self.font.render(str(kredit.credits), True, orange)
        screen.blit(
            credit_surface,
            (rect.x + 8, rect.bottom - credit_surface.get_height() - 2),
        )
        k_surface = small.render("K", True, gray)
        screen.blit(k_surface, (rect.right - k_surface.get_width() - 8, rect.y + 4))
        slot_surface = small.render(str(kredit.slots), True, gray)
        screen.blit(
            slot_surface,
            (rect.right - slot_surface.get_width() - 8, rect.bottom - slot_surface.get_height() - 3),
        )

    def _draw_own_hand(self, screen: Surface, ground: BattleGround) -> None:
        """绘制己方手牌"""
        own_hand = ground.hands[Player.A].cards
        self.last_hand_rects = {}
        now = pygame.time.get_ticks()
        request = ground.pending_selection
        base_rects = self.hand_rects(screen, len(own_hand))
        mouse = pygame.mouse.get_pos()
        hovered_index = -1
        if self.drag_card is None and request is None and ground.pending_choice is None:
            for index, rect in enumerate(base_rects):
                if rect.inflate(8, 8).collidepoint(mouse):
                    hovered_index = index
        count = len(own_hand)
        pivot_x = screen.get_width() / 2
        pivot_y = screen.get_height() * 1.5
        draw_order = list(range(count))
        if hovered_index >= 0:
            draw_order.remove(hovered_index)
            draw_order.append(hovered_index)
        for index in draw_order:
            rect = base_rects[index]
            card = own_hand[index]
            if any(anim_card is card for anim_card, _, _ in self.choice_move_anims):
                continue
            reveal = self.hand_reveal.get(id(card))
            if reveal is not None:
                if now < reveal:
                    continue
                self.hand_reveal.pop(id(card), None)
            dragging = card is self.drag_card and self.drag_from_hand
            selected = card is self.selected_hand
            hover_lift = int(self.card_h * 0.18) if index == hovered_index and not dragging else 0
            center_y = rect.y + self.card_h / 2
            radial = max(1.0, pivot_y - center_y)
            angle = -math.degrees(math.atan2(rect.centerx - pivot_x, radial)) * 0.55
            visual_rect = pygame.Rect(rect.x, rect.y - hover_lift, rect.width, rect.height)
            surface = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
            art = self._card_art(card)
            if art is None:
                art = self.face
            if art.get_size() != (self.card_w, self.card_h):
                art = pygame.transform.smoothscale(art, (self.card_w, self.card_h))
            surface.blit(art, (0, 0))
            self._draw_stats_overlay(surface, card, pygame.Rect(0, 0, self.card_w, self.card_h))
            border = (255, 210, 80) if (selected or dragging or index == hovered_index) else (220, 220, 220)
            pygame.draw.rect(
                surface,
                border,
                (0, 0, self.card_w, self.card_h),
                3 if (selected or dragging or index == hovered_index) else 2,
                border_radius=4,
            )
            rotated = pygame.transform.rotozoom(surface, angle, 1.0)
            visual_rect = rotated.get_rect(center=(rect.centerx, rect.y + self.card_h // 2 - hover_lift))
            self.last_hand_rects[id(card)] = visual_rect.copy()
            screen.blit(rotated, visual_rect)
            if card.revealed:
                size = max(14, int(self.card_w * 0.18))
                eye = pygame.transform.smoothscale(self.eye_image, (size, size))
                eye_pos = (visual_rect.x + 4, visual_rect.centery - size // 2)
                screen.blit(eye, eye_pos)
            if request is not None and card in self.selection_cards:
                self._draw_selection_stamp(screen, visual_rect)

    def _draw_status(self, screen: Surface, ground: BattleGround) -> None:
        """绘制双方指挥点、提示与结束回合按钮"""
        panel_x = self.margin
        self._draw_kredits(
            screen,
            ground,
            Player.B,
            panel_x,
            int(self.screen_size[1] * 0.30),
            "对手",
        )
        self._draw_kredits(
            screen,
            ground,
            Player.A,
            panel_x,
            int(self.screen_size[1] * 0.74),
            "我方",
        )
        self._place_end_button()
        self.end_button.update()
        screen.blit(self.end_button.image, self.end_button.rect)
        self._draw_notice(screen, ground)

    def _draw_notice(self, screen: Surface, ground: BattleGround) -> None:
        """
        在屏幕中央绘制横向渐变提示条

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        now = pygame.time.get_ticks()
        if ground.notice:
            self.message = ground.notice
            ground.notice = ""
        if self.message != self._last_message:
            self._last_message = self.message
            self.notice_start = now
            self.notice_until = now + 2000 if self.message else 0
        if not self.message or now >= self.notice_until:
            return
        fade = 1.0
        if now - self.notice_start < 250:
            fade = min(fade, (now - self.notice_start) / 250)
        if self.notice_until - now < 250:
            fade = min(fade, (self.notice_until - now) / 250)
        if fade <= 0:
            return
        text = self.message
        width = screen.get_width()
        bar_height = max(56, int(self.card_h * 0.34))
        if self.notice_surface is None or self.notice_surface_size != (width, bar_height):
            surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
            center = width / 2
            for x in range(width):
                ratio = abs(x - center) / center
                alpha = int(190 * max(0.0, 1.0 - ratio) ** 1.6)
                pygame.draw.line(surface, (0, 0, 0, alpha), (x, 0), (x, bar_height))
            self.notice_surface = surface
            self.notice_surface_size = (width, bar_height)
        y = screen.get_height() // 2 - bar_height // 2
        self.notice_surface.set_alpha(int(255 * fade))
        screen.blit(self.notice_surface, (0, y))
        text_surface = self.font.render(text, True, (240, 240, 240))
        text_surface.set_alpha(int(255 * fade))
        screen.blit(text_surface, text_surface.get_rect(center=(width // 2, y + bar_height // 2)))

    def _draw_winner(self, screen: Surface, ground: BattleGround) -> None:
        """绘制胜负遮罩与继续按钮"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        text = "胜利" if ground.winner is Player.A else "失败"
        color = (255, 220, 120) if ground.winner is Player.A else (230, 120, 120)
        center = (screen.get_width() // 2, screen.get_height() // 2 - int(self.card_h * 0.3))
        self._text(screen, text, center, color, self.big_font, center=True)
        self.continue_button.rect.center = (
            screen.get_width() // 2,
            screen.get_height() // 2 + int(self.card_h * 0.25),
        )
        self.continue_button.update()
        screen.blit(self.continue_button.image, self.continue_button.rect)

    def _draw_deck_add_anims(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制卡牌飞向牌堆并加入的动画

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if not self.deck_add_anims:
            return
        now = pygame.time.get_ticks()
        duration = 560
        alive: list[tuple[Card, pygame.Rect, int]] = []
        for card, start_rect, start_time in self.deck_add_anims:
            elapsed = now - start_time
            if elapsed < 0:
                alive.append((card, start_rect, start_time))
                continue
            if elapsed >= duration:
                continue
            alive.append((card, start_rect, start_time))
            progress = elapsed / duration
            ease = progress * progress
            deck_rect = self.deck_rect if card.owner is Player.A else self.deck_rect_b
            if deck_rect is None:
                target = (screen.get_width() // 2, 20)
            else:
                target = deck_rect.center
            x = start_rect.centerx + (target[0] - start_rect.centerx) * ease
            y = start_rect.centery + (target[1] - start_rect.centery) * ease
            y -= 80 * math.sin(math.pi * progress)
            art = self._card_art(card) if card.owner is Player.A else None
            image = art if art is not None else self.deck_back
            angle = -28 * progress
            rotated = pygame.transform.rotate(image, angle)
            if progress > 0.82:
                rotated.set_alpha(int(255 * (1 - (progress - 0.82) / 0.18)))
            rect = rotated.get_rect(center=(int(x), int(y)))
            screen.blit(rotated, rect)
        self.deck_add_anims = alive

    def _draw_decks(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制双方牌堆, 斜放的卡背加剩余数量

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        back = pygame.transform.rotate(self.deck_back, -14)
        width, height = self.screen_size
        positions = (
            (Player.B, self.margin, int(height * 0.012), "对手卡组"),
            (
                Player.A,
                width - self.margin - back.get_width(),
                self.status_y - back.get_height() - int(height * 0.010),
                "我方卡组",
            ),
        )
        for player, x, y, label in positions:
            now = pygame.time.get_ticks()
            start = self.shuffle_anims.get(player)
            if start is not None:
                elapsed = now - start
                if elapsed >= 1500:
                    self.shuffle_anims.pop(player, None)
                    start = None
                else:
                    self._draw_shuffle_pile(screen, x, y, elapsed, player)
            if start is None:
                screen.blit(back, (x, y))
            if player is Player.A:
                self.deck_rect = pygame.Rect(x, y, back.get_width(), back.get_height())
            else:
                self.deck_rect_b = pygame.Rect(x, y, back.get_width(), back.get_height())
            count = len(ground.decks[player].cards)
            label_y = y - 24 if player is Player.A else y + back.get_height() + 2
            self._text(screen, f"{label} {count}", (x, label_y), (215, 215, 215))

    def _draw_shuffle_pile(
        self,
        screen: Surface,
        x: int,
        y: int,
        elapsed: int,
        player: Player,
    ) -> None:
        """
        绘制俯视角切牌洗切动画

        Args:
            screen: 屏幕 Surface
            x: 牌堆横坐标
            y: 牌堆纵坐标
            elapsed: 已进行时间
            player: 牌堆所有者
        """
        duration = 1500
        progress = elapsed / duration
        cycle = elapsed % 450
        spread = math.sin((cycle / 450) * math.pi)
        fade = max(0.0, 1 - max(0.0, (progress - 0.85) / 0.15))
        for index in range(6):
            pile = -1 if index < 3 else 1
            level = index % 3
            offset_x = int(pile * 18 * spread)
            offset_y = int(pile * 70 * spread + level * 11 - (8 if pile < 0 else 0))
            angle = -14 + pile * 10 * spread + (level - 1) * 3
            image = pygame.transform.rotate(self.deck_back, angle)
            image.set_alpha(int(255 * fade))
            screen.blit(image, (x + offset_x, y + offset_y))

    def _draw_return_anims(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制单位回手动画: 先在原位置短暂停留, 再飞向手牌

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if not self.return_anims:
            return
        now = pygame.time.get_ticks()
        duration = 520
        alive: list[tuple[Card, pygame.Rect, int]] = []
        hand_a = self.hand_rects(screen, len(ground.hands[Player.A].cards))
        target_a = hand_a[-1].center if hand_a else (screen.get_width() // 2, self.own_hand_y + self.card_h // 2)
        target_b = (screen.get_width() // 2, self.opp_hand_y + self.opp_hand_h // 2)
        for card, old_rect, start in self.return_anims:
            if now < start:
                alive.append((card, old_rect, start))
                continue
            progress = (now - start) / duration
            if progress >= 1:
                continue
            alive.append((card, old_rect, start))
            ease = 1 - (1 - progress) ** 3
            target = target_a if card.controller is Player.A else target_b
            x = int(old_rect.centerx + (target[0] - old_rect.centerx) * ease)
            y = int(old_rect.centery + (target[1] - old_rect.centery) * ease)
            y -= int(22 * math.sin(math.pi * progress))
            art = self._card_art(card)
            image = (art if art is not None else self.face).copy()
            image.set_alpha(int(255 * (1 - progress * 0.35)))
            screen.blit(image, image.get_rect(center=(x, y)))
        self.return_anims = alive

    def _draw_draw_anims(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制抽牌时从牌堆飞向手牌的卡背

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if not self.draw_anims:
            return
        now = pygame.time.get_ticks()
        duration = 320
        hand_rects = self.hand_rects(screen, len(ground.hands[Player.A].cards))
        if hand_rects:
            target_a = hand_rects[-1].center
        else:
            target_a = (screen.get_width() // 2, self.own_hand_y + self.card_h // 2)
        target_b = (screen.get_width() // 2, self.opp_hand_y + self.opp_hand_h // 2)
        alive: list[tuple[Player, int]] = []
        for player, start in self.draw_anims:
            if now < start:
                alive.append((player, start))
                continue
            progress = (now - start) / duration
            if progress >= 1:
                continue
            alive.append((player, start))
            if player is Player.A:
                source = self.deck_rect.center if self.deck_rect is not None else None
                target = target_a
            else:
                source = self.deck_rect_b.center if self.deck_rect_b is not None else None
                target = target_b
            if source is None:
                continue
            x = int(source[0] + (target[0] - source[0]) * progress)
            y = int(source[1] + (target[1] - source[1]) * progress)
            ghost = self.deck_back.copy()
            ghost.set_alpha(int(255 * (1 - progress * 0.6)))
            screen.blit(ghost, ghost.get_rect(center=(x, y)))
        self.draw_anims = alive

    def _draw_discard_anims(self, screen: Surface) -> None:
        """
        绘制弃牌特效: 升空停顿后向右倾斜飞出

        Args:
            screen: 屏幕 Surface
        """
        self._draw_fly_cards(screen, self.discard_anims, 1000, 120, 1, -35)

    def _draw_remove_anims(self, screen: Surface) -> None:
        """
        绘制移除特效: 升空较低, 停顿后向左倾斜飞出

        Args:
            screen: 屏幕 Surface
        """
        self._draw_fly_cards(screen, self.remove_anims, 900, 80, -1, 35)

    def _draw_move_anims(self, screen: Surface) -> None:
        """
        绘制单位非线性移动动画

        Args:
            screen: 屏幕 Surface
        """
        if not self.move_anims:
            return
        now = pygame.time.get_ticks()
        duration = 420
        alive: dict[int, tuple[Card, pygame.Rect, int]] = {}
        for key, (card, old_rect, start) in self.move_anims.items():
            record = self.frame_rects.get(key)
            if record is None or card.line is None:
                continue
            if now < start:
                alive[key] = (card, old_rect, start)
                continue
            elapsed = now - start
            if elapsed >= duration:
                continue
            alive[key] = (card, old_rect, start)
            progress = elapsed / duration
            ease = 1 - (1 - progress) ** 3
            new_rect = record[1]
            x = old_rect.centerx + (new_rect.centerx - old_rect.centerx) * ease
            y = old_rect.centery + (new_rect.centery - old_rect.centery) * ease
            y -= int(30 * math.sin(math.pi * progress))
            art = self._card_art(card)
            image = art if art is not None else self.face
            rect = image.get_rect(center=(int(x), int(y)))
            screen.blit(image, rect)
        self.move_anims = alive

    def _draw_slam_anims(self, screen: Surface) -> None:
        """
        绘制大拍桌: 卡牌升空停留后重砸落下

        Args:
            screen: 屏幕 Surface
        """
        if not self.slam_anims:
            return
        now = pygame.time.get_ticks()
        total = 1050
        impact = 800
        for key, (card, rect, start) in list(self.slam_anims.items()):
            if card.line is None:
                self.slam_anims.pop(key, None)
                self.slam_impacted.discard(key)
                continue
            if rect is None:
                record = self.frame_rects.get(key)
                if record is None:
                    continue
                rect = record[1]
                self.slam_anims[key] = (card, rect, start)
            elapsed = now - start
            if elapsed >= total:
                self.slam_anims.pop(key, None)
                self.slam_impacted.discard(key)
                continue
            if elapsed < 180:
                scale = 0.8 + 0.3 * (elapsed / 180)
            elif elapsed < 500:
                scale = 1.1 - 0.1 * ((elapsed - 180) / 320)
            else:
                scale = 1.0
            if card.line.kind is LineKind.FRONT:
                line_y = self.front_y
            else:
                line_y = self.own_line_y if card.controller is Player.A else self.opp_line_y
            hover_y = line_y - int(self.card_h * 0.80)
            hover_offset = hover_y - rect.y
            if elapsed < 180:
                offset = hover_offset
            elif elapsed < 500:
                offset = hover_offset + int(8 * math.sin((elapsed - 180) / 45))
            elif elapsed < impact:
                t = (elapsed - 500) / (impact - 500)
                offset = int(hover_offset * (1 - t**3))
            else:
                offset = 0
            shadow_alpha = int(180 * (1 - min(1.0, abs(offset) / max(1, abs(hover_offset)))))
            shadow = pygame.Surface((rect.width, max(8, rect.height // 6)), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect())
            screen.blit(shadow, shadow.get_rect(center=(rect.centerx, rect.bottom + 6)))
            art = self._card_art(card)
            image = art if art is not None else self.face
            width = max(1, int(rect.width * scale))
            height = max(1, int(rect.height * scale))
            scaled = pygame.transform.smoothscale(image, (width, height))
            center = (rect.centerx, rect.centery + offset)
            screen.blit(scaled, scaled.get_rect(center=center))
            border = pygame.Rect(0, 0, width, height)
            border.center = center
            pygame.draw.rect(screen, (235, 235, 235), border, 2, border_radius=4)
            if elapsed >= impact and key not in self.slam_impacted:
                self.slam_impacted.add(key)
                self.shake_until = now + 1200
                self.shake_strength = max(20, int(self.card_h * 0.22))
                self.slam_waves.append((rect.copy(), now))

    def _draw_slam_waves(self, screen: Surface) -> None:
        """
        绘制大拍桌落地时的冲击波

        Args:
            screen: 屏幕 Surface
        """
        if not self.slam_waves:
            return
        now = pygame.time.get_ticks()
        alive: list[tuple[pygame.Rect, int]] = []
        for rect, start in self.slam_waves:
            progress = (now - start) / 320
            if progress >= 1:
                continue
            alive.append((rect, start))
            width = max(24, int(rect.width * (1 + progress * 1.2)))
            height = max(8, int(width * 0.24))
            wave = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                wave,
                (255, 220, 150, int(150 * (1 - progress))),
                (0, 0, width, height),
                3,
            )
            screen.blit(wave, wave.get_rect(center=(rect.centerx, rect.bottom - 4)))
        self.slam_waves = alive

    def _draw_fly_cards(
        self,
        screen: Surface,
        anims: list[tuple[Card, pygame.Rect, int]],
        duration: int,
        rise: int,
        direction: int,
        angle_max: float,
    ) -> None:
        """
        绘制卡牌起飞、停顿、倾斜飞出的动画

        Args:
            screen: 屏幕 Surface
            anims: (卡牌, 起始矩形, 开始时间) 列表
            duration: 总时长
            rise: 上升高度
            direction: 飞出方向, 1 向右, -1 向左
            angle_max: 最终倾斜角度
        """
        if not anims:
            return
        now = pygame.time.get_ticks()
        alive: list[tuple[Card, pygame.Rect, int]] = []
        for card, rect, start in anims:
            if now < start:
                alive.append((card, rect, start))
                continue
            elapsed = now - start
            if elapsed > duration:
                continue
            alive.append((card, rect, start))
            art = self._card_art(card)
            image = (art if art is not None else self.face).copy()
            progress = elapsed / duration
            if progress < 0.3:
                t = progress / 0.3
                lift = int(rise * (1 - (1 - t) ** 2))
                x, y = rect.centerx, rect.centery - lift
                angle = 0.0
                alpha = 255
            elif progress < 0.5:
                x, y = rect.centerx, rect.centery - rise
                angle = 0.0
                alpha = 255
            else:
                t = (progress - 0.5) / 0.5
                x = rect.centerx + direction * int(t * t * screen.get_width() * 0.9)
                y = rect.centery - rise + int(t * 60)
                angle = angle_max * t
                alpha = int(255 * (1 - t))
            rotated = pygame.transform.rotate(image, angle)
            rotated.set_alpha(max(0, alpha))
            screen.blit(rotated, rotated.get_rect(center=(int(x), int(y))))
        anims[:] = alive

    def _start_drag(self, card: Card, from_hand: bool, origin: pygame.Rect, pos: tuple[int, int]) -> None:
        """
        开始拖拽

        Args:
            card: 被拖拽的卡牌
            from_hand: 是否来自手牌
            origin: 起始矩形
            pos: 鼠标位置
        """
        self.drag_card = card
        self.drag_from_hand = from_hand
        self.drag_origin = origin.copy()
        self.drag_pos = pos
        self.selected_hand = None
        self.selected_unit = None
        self.message = ""

    def _line_area(self, screen: Surface, y: int) -> pygame.Rect:
        """
        返回一条战线可放置卡牌的区域, 按最大卡位数取范围

        Args:
            screen: 屏幕 Surface
            y: 战线纵坐标

        Returns:
            区域矩形
        """
        rects = self.line_rects(screen, self.MAX_SLOTS, y)
        area = rects[0].copy()
        for rect in rects[1:]:
            area.union_ip(rect)
        return area

    def _drop_index(self, screen: Surface, pos: tuple[int, int], line: Line) -> int:
        """
        根据鼠标横坐标计算插入位置

        Args:
            screen: 屏幕 Surface
            pos: 鼠标位置
            line: 目标战线

        Returns:
            插入位置, 0 到当前卡位数(含总部)
        """
        count = len(self._sequence(line)) + 1
        rects = self.line_rects(screen, count, 0)
        centers = [rect.centerx for rect in rects]
        return min(range(count), key=lambda i: abs(centers[i] - pos[0]))

    def _preview_target(self, screen: Surface, ground: BattleGround) -> tuple[Line | None, int | None]:
        """
        计算当前拖拽的预览目标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数

        Returns:
            (目标战线, 插入位置), 无有效目标时为 (None, None)
        """
        if self.drag_card is None or self.drag_pos is None or ground.winner is not None:
            return None, None
        if ground.turn_owner is not Player.A:
            return None, None
        pos = self.drag_pos
        support = ground.support_lines[Player.A]
        front = ground.front_line
        support_area = self._line_area(screen, self.own_line_y)
        front_area = self._line_area(screen, self.front_y)
        if self.drag_from_hand:
            if self.drag_card.is_unit and support_area.collidepoint(pos):
                if len(support.units) < support.capacity:
                    return support, self._drop_index(screen, pos, support)
            return None, None
        if self.drag_card.line is support:
            if (
                front_area.collidepoint(pos)
                and len(front.units) < front.capacity
                and front.owner in (None, Player.A)
            ):
                return front, self._drop_index(screen, pos, front)
            return None, None
        if self.drag_card.line is front:
            if support_area.collidepoint(pos) and len(support.units) < support.capacity:
                return support, self._drop_index(screen, pos, support)
            return None, None
        return None, None

    def on_mouse_down(self, pos: tuple[int, int], screen: Surface, ground: BattleGround) -> None:
        """
        按下左键: 结束回合按钮或开始拖拽

        Args:
            pos: 鼠标位置
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if ground.winner is not None:
            if self.continue_button.rect.collidepoint(pos):
                self._continue_after_match()
            return
        if ground.pending_choose is not None:
            for rect, option in self.choose_rects:
                if rect.collidepoint(pos):
                    ground.resolve_choose(option)
                    return
            ground.cancel_choose()
            return
        if ground.pending_choice is not None:
            if self.end_button.rect.collidepoint(pos):
                self._end_turn()
                return
            for rect, card in self.choice_rects:
                if rect.collidepoint(pos):
                    ground.resolve_card_choice(card)
                    return
            return
        request = ground.pending_selection
        if request is not None and request.player is Player.A:
            if self.confirm_rect is not None and self.confirm_rect.collidepoint(pos):
                if request.min_count <= len(self.selection_cards) <= request.max_count:
                    if ground.resolve_selection(list(self.selection_cards)):
                        self.selection_cards.clear()
                return
            if self.end_button.rect.collidepoint(pos):
                self._end_turn()
                return
            own_hand = ground.hands[Player.A].cards
            for rect, card in zip(self.hand_rects(screen, len(own_hand)), own_hand):
                if not rect.collidepoint(pos):
                    continue
                if request.filter is not None and not request.filter(card):
                    return
                if card in self.selection_cards:
                    self.selection_cards.remove(card)
                elif len(self.selection_cards) < request.max_count:
                    self.selection_cards.append(card)
                return
            return
        if ground.pending_target is not None:
            self._clear_drag()
            if pos[1] >= self.own_hand_y:
                ground.cancel_target()
                return
            target = self._pending_target_at(screen, pos, ground)
            if target is not None:
                pending_card = ground.pending_target.source
                if ground.resolve_target(target):
                    self.message = "指令已使用" if pending_card.type is CardType.ORDER else ""
            return
        if self.end_button.rect.collidepoint(pos):
            self._end_turn()
            return
        if ground.turn_owner is not Player.A:
            return
        own_hand = ground.hands[Player.A].cards
        for rect, card in zip(self.hand_rects(screen, len(own_hand)), own_hand):
            if rect.collidepoint(pos):
                if card.type is CardType.ORDER and card.targeted:
                    self.preview_card = card
                self._start_drag(card, True, rect, pos)
                return
        for line, y in ((ground.support_lines[Player.A], self.own_line_y), (ground.front_line, self.front_y)):
            for rect, card in self.line_units(screen, line, y):
                if rect.collidepoint(pos) and card.controller is Player.A:
                    self._start_drag(card, False, rect, pos)
                    return

    def _preview_target_at(
        self, screen: Surface, pos: tuple[int, int], ground: BattleGround
    ) -> Card | None:
        """
        返回指向预览状态下鼠标处的合法目标

        Args:
            screen: 屏幕 Surface
            pos: 鼠标位置
            ground: 战斗全局参数

        Returns:
            合法目标, 没有时为 None
        """
        card = self.preview_card
        if card is None or card.target_valid is None:
            return None
        for line, y in (
            (ground.support_lines[Player.A], self.own_line_y),
            (ground.support_lines[Player.B], self.opp_line_y),
            (ground.front_line, self.front_y),
        ):
            for rect, unit in self.line_units(screen, line, y):
                if rect.collidepoint(pos) and card.target_valid(unit, Player.A, ground):
                    return unit
        for player, y in ((Player.A, self.own_line_y), (Player.B, self.opp_line_y)):
            hq = ground.hqs[player]
            rect = self.hq_rect(screen, ground.support_lines[player], y)
            if rect.collidepoint(pos) and card.target_valid(hq, Player.A, ground):
                return hq
        return None

    def _pending_target_at(
        self, screen: Surface, pos: tuple[int, int], ground: BattleGround
    ) -> Card | None:
        """
        返回指向状态下鼠标处的合法目标

        Args:
            screen: 屏幕 Surface
            pos: 鼠标位置
            ground: 战斗全局参数

        Returns:
            合法目标, 没有时为 None
        """
        pending = ground.pending_target
        if pending is None:
            return None
        for line, y in (
            (ground.support_lines[Player.A], self.own_line_y),
            (ground.support_lines[Player.B], self.opp_line_y),
            (ground.front_line, self.front_y),
        ):
            for rect, card in self.line_units(screen, line, y):
                if rect.collidepoint(pos) and pending.valid(card):
                    return card
        for player, y in ((Player.A, self.own_line_y), (Player.B, self.opp_line_y)):
            hq = ground.hqs[player]
            rect = self.hq_rect(screen, ground.support_lines[player], y)
            if rect.collidepoint(pos) and pending.valid(hq):
                return hq
        return None

    def _target_at(
        self, screen: Surface, pos: tuple[int, int], ground: BattleGround
    ) -> tuple[Card | None, pygame.Rect | None]:
        """
        返回鼠标下可攻击的敌方单位或总部

        Args:
            screen: 屏幕 Surface
            pos: 鼠标位置
            ground: 战斗全局参数

        Returns:
            (目标, 矩形), 无合法目标时为 (None, None)
        """
        attacker = self.drag_card
        if attacker is None:
            return None, None
        for line, y in (
            (ground.support_lines[Player.B], self.opp_line_y),
            (ground.front_line, self.front_y),
        ):
            for rect, card in self.line_units(screen, line, y):
                if (
                    rect.collidepoint(pos)
                    and card.controller is Player.B
                    and ground.can_attack(Player.A, attacker, card)
                ):
                    return card, rect
        hq_rect = self.hq_rect(screen, ground.support_lines[Player.B], self.opp_line_y)
        if hq_rect.collidepoint(pos) and ground.can_attack(Player.A, attacker, ground.hqs[Player.B]):
            return ground.hqs[Player.B], hq_rect
        return None, None

    def on_mouse_move(self, pos: tuple[int, int], screen: Surface, ground: BattleGround) -> None:
        """
        拖动中更新鼠标位置与高亮目标

        Args:
            pos: 鼠标位置
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if self.drag_card is None:
            return
        self.drag_pos = pos
        if self.drag_from_hand:
            self.hover_target = None
            self.hover_rect = None
        else:
            self.hover_target, self.hover_rect = self._target_at(screen, pos, ground)

    def _attack(self, ground: BattleGround, card: Card, target: Card) -> None:
        """
        尝试攻击并给出提示

        Args:
            ground: 战斗全局参数
            card: 攻击单位
            target: 目标
        """
        if not ground.can_attack(Player.A, card, target):
            reason = ground.action_block_reason(card, "attack")
            self.message = reason or "无法攻击：目标不合法或不在攻击范围内"
            return
        if ground.attack_unit(Player.A, card, target):
            self.message = ""
        else:
            self.message = "无法攻击：目标不合法或不在攻击范围内"

    def on_mouse_up(self, pos: tuple[int, int], screen: Surface, ground: BattleGround) -> None:
        """
        松开左键: 结算拖拽

        Args:
            pos: 鼠标位置
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if ground.pending_choice is not None:
            self._clear_drag()
            return
        if ground.pending_selection is not None:
            self._clear_drag()
            return
        if self.preview_card is not None:
            card = self.preview_card
            target = self._preview_target_at(screen, pos, ground)
            self.preview_card = None
            self._clear_drag()
            if target is None:
                self.message = "已取消指向"
                return
            if not ground.use_card(Player.A, card):
                self.message = ground.use_block_reason(Player.A, card) or "无法使用该指令"
                return
            if ground.pending_target is not None and not ground.resolve_target(target):
                ground.cancel_target()
                self.message = "已取消指向"
                return
            self.message = "指令已使用"
            return
        if ground.pending_target is not None:
            self._clear_drag()
            if pos[1] >= self.own_hand_y:
                ground.cancel_target()
            return
        card = self.drag_card
        from_hand = self.drag_from_hand
        if card is None:
            self._clear_drag()
            return
        try:
            if ground.winner is not None or ground.turn_owner is not Player.A:
                return
            own_support = ground.support_lines[Player.A]
            front = ground.front_line
            support_area = self._line_area(screen, self.own_line_y)
            front_area = self._line_area(screen, self.front_y)

            if from_hand:
                if card.type is CardType.ORDER:
                    if pos[1] < self.own_hand_y:
                        origin = self.drag_origin or pygame.Rect(0, 0, self.card_w, self.card_h)
                        if ground.use_card(Player.A, card):
                            if ground.pending_choose is not None:
                                self.message = "请选择一项"
                            elif ground.pending_target is not None:
                                self.message = "选择目标"
                            else:
                                self.message = "指令已使用"
                                self._add_order_anim(origin)
                        else:
                            self.message = ground.use_block_reason(Player.A, card) or "无法使用该指令"
                    self._clear_drag()
                    return
                if support_area.collidepoint(pos):
                    index = self._drop_index(screen, pos, own_support)
                    if ground.use_card(Player.A, card, index):
                        if ground.pending_target is not None:
                            self.message = "选择目标"
                        else:
                            self.message = ""
                    else:
                        self.message = ground.use_block_reason(Player.A, card) or "无法部署该单位"
                self._clear_drag()
                return

            for rect, target in self.line_units(screen, ground.support_lines[Player.B], self.opp_line_y):
                if rect.collidepoint(pos):
                    self._attack(ground, card, target)
                    return
            if self.hq_rect(screen, ground.support_lines[Player.B], self.opp_line_y).collidepoint(pos):
                self._attack(ground, card, ground.hqs[Player.B])
                return
            for rect, target in self.line_units(screen, front, self.front_y):
                if rect.collidepoint(pos) and target.controller is Player.B:
                    self._attack(ground, card, target)
                    return
            if support_area.collidepoint(pos):
                if card.line is own_support:
                    self.message = "不能在同一战线内移动"
                    return
                index = self._drop_index(screen, pos, own_support)
                if ground.move_unit(Player.A, card, own_support, index):
                    self.message = "单位已移动"
                else:
                    self.message = ground.action_block_reason(card, "move") or "无法移动该单位"
                return
            if front_area.collidepoint(pos):
                if card.line is front:
                    self.message = "不能在同一战线内移动"
                    return
                index = self._drop_index(screen, pos, front)
                if ground.move_unit(Player.A, card, front, index):
                    self.message = "单位已移动到前线"
                else:
                    self.message = ground.action_block_reason(card, "move") or "无法移动该单位"
        finally:
            self._clear_drag()

    def _clear_drag(self) -> None:
        """清空拖拽状态"""
        self.drag_card = None
        self.drag_from_hand = False
        self.drag_origin = None
        self.drag_pos = None
        self.hover_target = None
        self.hover_rect = None

    def _draw_drag(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制拖拽中的红色箭头

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if self.drag_card is None or self.drag_pos is None or self.drag_origin is None:
            return
        if self.drag_card.type is CardType.ORDER and not self.drag_card.targeted:
            return
        start = self.drag_origin.center
        end = self.drag_pos
        color = (225, 60, 60)
        width = max(3, self.card_w // 40)
        pygame.draw.line(screen, color, start, end, width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        size = max(12, self.card_w // 7)
        left = (end[0] - size * math.cos(angle - 0.42), end[1] - size * math.sin(angle - 0.42))
        right = (end[0] - size * math.cos(angle + 0.42), end[1] - size * math.sin(angle + 0.42))
        pygame.draw.polygon(screen, color, [end, left, right])

    def _draw_drag_ghost(self, screen: Surface) -> None:
        """
        在鼠标位置绘制半透明的拖拽手牌, 场上单位不跟随鼠标

        Args:
            screen: 屏幕 Surface
        """
        if self.drag_card is None or self.drag_pos is None or not self.drag_from_hand:
            return
        if self.drag_card.targeted:
            return
        art = self._card_art(self.drag_card) or self.face
        ghost = art.copy()
        ghost.set_alpha(120)
        rect = ghost.get_rect(center=self.drag_pos)
        screen.blit(ghost, rect)
        self._draw_stats_overlay(screen, self.drag_card, rect)
        pygame.draw.rect(screen, (255, 210, 80), rect, 2, border_radius=4)

    def _draw_preview_target(self, screen: Surface, ground: BattleGround) -> None:
        """
        指向预览时高亮鼠标下的合法目标

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        if self.preview_card is None:
            return
        target = self._preview_target_at(screen, pygame.mouse.get_pos(), ground)
        if target is None:
            return
        record = self.frame_rects.get(id(target))
        if record is not None:
            pygame.draw.rect(screen, (235, 70, 70), record[1], 3, border_radius=4)

    def _draw_target_arrow(self, screen: Surface, ground: BattleGround) -> None:
        """
        绘制指向状态的红色箭头与目标高亮

        Args:
            screen: 屏幕 Surface
            ground: 战斗全局参数
        """
        pending = ground.pending_target
        if pending is None:
            return
        record = self.frame_rects.get(id(pending.source))
        if record is not None:
            start = record[1].center
        elif pending.source.type is CardType.ORDER:
            start = self.order_origins.get(id(pending.source), pygame.mouse.get_pos())
        else:
            start = (screen.get_width() // 2, self.front_y + self.card_h // 2)
        end = pygame.mouse.get_pos()
        color = (235, 70, 70)
        pygame.draw.line(screen, color, start, end, 4)
        direction = pygame.Vector2(end) - pygame.Vector2(start)
        if direction.length_squared() > 0:
            direction = direction.normalize()
            normal = pygame.Vector2(-direction.y, direction.x)
            tip = pygame.Vector2(end)
            left = tip - direction * 18 + normal * 9
            right = tip - direction * 18 - normal * 9
            pygame.draw.polygon(screen, color, [tuple(tip), tuple(left), tuple(right)])
        hovered = self._pending_target_at(screen, end, ground)
        if hovered is not None:
            hovered_rect = self.frame_rects.get(id(hovered))
            if hovered_rect is not None:
                pygame.draw.rect(screen, color, hovered_rect[1], 3, border_radius=4)
        self._text(
            screen,
            "选择目标, 点击手牌取消",
            (screen.get_width() // 2, self.own_hand_y - 26),
            (240, 190, 100),
            center=True,
        )

# ==================== 主循环 ====================


def draw_battle(screen: Surface, font: Font) -> None:
    """
    绘制战斗场景

    Args:
        screen: 屏幕 Surface
        font: 提示文字字体
    """
    ground = Global.battle_ground
    ui = Global.battle_ui
    if ground is None or ui is None:
        screen.fill((18, 22, 20))
        text = font.render("战斗未初始化", True, (200, 200, 200))
        screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
        return
    ui.draw(screen, ground)


def loop(
    screen: Surface,
    start_button: Surface,
    start_button_hover: Surface,
    card_button: Surface,
    card_button_hover: Surface,
    start_rect: pygame.Rect,
    card_rect: pygame.Rect,
    background: Surface,
    button_group: ButtonGroup,
    font: Font,
    dt: int = 0,
) -> None:
    """
    处理一帧的事件与绘制

    Args:
        screen: 屏幕 Surface
        start_button: 开始按钮图标
        start_button_hover: 开始按钮悬浮图标
        card_button: 卡牌按钮图标
        card_button_hover: 卡牌按钮悬浮图标
        start_rect: 开始按钮位置
        card_rect: 卡牌按钮位置
        background: 开始界面背景图
        button_group: 开始界面选项按钮组
        font: 通用中文字体
        dt: 距上一帧的毫秒数
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Global.status.quitting = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            Global.status.quitting = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Global.status.scene == SCENE_MENU:
                handle_menu_click(event.pos, start_rect, card_rect)
            elif Global.status.scene == SCENE_START:
                button_group.handle_event(event)
            elif Global.status.scene == SCENE_BATTLE:
                ground = Global.battle_ground
                ui = Global.battle_ui
                if ground is not None and ui is not None:
                    ui.on_mouse_down(event.pos, screen, ground)
        elif event.type == pygame.MOUSEMOTION:
            if Global.status.scene == SCENE_BATTLE:
                ground = Global.battle_ground
                ui = Global.battle_ui
                if ground is not None and ui is not None:
                    ui.on_mouse_move(event.pos, screen, ground)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if Global.status.scene == SCENE_BATTLE:
                ground = Global.battle_ground
                ui = Global.battle_ui
                if ground is not None and ui is not None:
                    ui.on_mouse_up(event.pos, screen, ground)
        elif event.type == BATTLE_START:
            logger.info(
                "战斗开始 host=%s guest=%s host_country=%s guest_country=%s",
                event.host,
                event.guest,
                event.host_country,
                event.guest_country,
            )

    if Global.status.scene == SCENE_MENU:
        draw_menu(
            screen,
            start_button,
            start_button_hover,
            card_button,
            card_button_hover,
            start_rect,
            card_rect,
        )
    elif Global.status.scene == SCENE_START:
        draw_start(screen, background, button_group)
    elif Global.status.scene == SCENE_BATTLE:
        ground = Global.battle_ground
        if ground is not None:
            ground.update(dt)
        if Global.battle_ui is not None:
            Global.battle_ui.update(dt)
        draw_battle(screen, font)
    pygame.display.flip()


def main() -> None:
    """程序入口函数, 创建窗口并驱动主循环"""
    start_time = time.perf_counter()
    LogManager().setup()
    sys.excepthook = CrashReporter()
    logger.info("程序启动")
    load_mods()
    save = load_or_create_save()
    Global.save_data = save
    Global.FPS = save.fps
    logger.info("mod 加载完成: %.1f ms", (time.perf_counter() - start_time) * 1000)
    screen = setup()
    logger.info("窗口创建完成: %.1f ms", (time.perf_counter() - start_time) * 1000)

    assets = Path(__file__).resolve().parent / "mods" / "kards" / "assets"
    loader = ImageLoader()
    button_size = 160
    button_gap = 24
    start_button = pygame.transform.smoothscale(
        loader.load(assets / "ui" / "开始按钮.png"),
        (button_size, button_size),
    )
    start_button_hover = start_button.copy()
    start_button_hover.fill((60, 60, 60, 0), special_flags=pygame.BLEND_RGB_ADD)

    # 卡牌按钮使用卡背的中心正方形作为图标
    card_back = loader.load(assets / "cards" / "card_back.png")
    side = min(card_back.get_width(), card_back.get_height())
    card_icon = card_back.subsurface(
        pygame.Rect(
            (card_back.get_width() - side) // 2,
            (card_back.get_height() - side) // 2,
            side,
            side,
        )
    ).copy()
    card_button = pygame.transform.smoothscale(card_icon, (button_size, button_size))
    card_button_hover = card_button.copy()
    card_button_hover.fill((60, 60, 60, 0), special_flags=pygame.BLEND_RGB_ADD)

    background = pygame.transform.smoothscale(
        loader.load(assets / "ui" / "开始背景.png"), screen.get_size()
    )
    start_y = (screen.get_height() - button_size * 2 - button_gap) // 2
    start_rect = pygame.Rect(40, start_y, button_size, button_size)
    card_rect = pygame.Rect(
        40,
        start_y + button_size + button_gap,
        button_size,
        button_size,
    )
    font = load_font(36)
    button_group = make_start_buttons(screen.get_width(), screen.get_height(), font)
    Global.battle_ui = BattleUI(loader, assets, font)
    logger.info("启动完成, 总用时: %.1f ms", (time.perf_counter() - start_time) * 1000)

    clock = Clock()
    while not Global.status.quitting:
        dt = clock.tick(Global.FPS)
        loop(
            screen,
            start_button,
            start_button_hover,
            card_button,
            card_button_hover,
            start_rect,
            card_rect,
            background,
            button_group,
            font,
            dt,
        )
    logger.info("程序退出")
    pygame.quit()



if __name__ == "__main__":
    main()
