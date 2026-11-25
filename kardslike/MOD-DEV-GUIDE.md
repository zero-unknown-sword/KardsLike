# KardsLike Mod 开发指南

本文档面向 `kardslike/mods/` 下的 Mod 开发者

## 1. 目录结构

一个 Mod 的推荐结构

```text
mods/
└── my_mod/
    ├── info.json
    ├── replace.json
    ├── code/
    │   ├── __init__.py
    │   ├── keywords/
    │   │   ├── __init__.py
    │   │   └── my_keyword.py
    │   └── cards/
    │       ├── Germany/
    │       │   └── card_example.py
    │       └── Soviet/
    │           └── card_example.py
    ├── data/
    │   └── zh.json
    └── assets/
        ├── cards/
        └── keyword/
```

## 2. info.json

```json
{
  "name": "My Mod",
  "author": "your name",
  "description": "mod 简介",
  "dependencies": ["kards"]
}
```

`dependencies` 中的 Mod 会先加载

## 3. 关键词

关键词定义文件放在 `code/keywords/` 下, 文件名就是关键词 id

```python
"""示例关键词"""
from main import KeywordData

KEYWORD = KeywordData(
    name="示例",
    description="示例关键词说明",
    icon="example.png",
    procedures=[],
)
```

带数值的关键词使用 `with_val`

```python
from main import KeywordData

KEYWORD = KeywordData(
    name="重甲",
    description="受到的对战伤害减少数值",
)

# 卡牌注册时
keywords=[KEYWORD.with_val(2)]
```

关键词也可以定义流程

```python
from main import CardTag, EventType, KeywordData, Procedure

KEYWORD = KeywordData(
    name="闪击",
    description="部署当回合可以行动",
    procedures=[
        Procedure(
            EventType.ENTER,
            lambda card, event, ground: event.card is card,
            lambda card, event, ground: card.remove_tag(
                CardTag.CANNOT_ACT_WHEN_ENTER
            ),
        )
    ],
)
```

## 4. 卡牌文件

卡牌放在 `code/cards/{Country}/` 下

```python
"""示例卡牌"""
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
    Event,
    EventType,
    Procedure,
    Rarity,
)


def action(card: Card, event: Event, ground: BattleGround) -> None:
    ground.draw(event.player)


CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.GERMANY,
    cost=1,
    display_name="示例卡牌",
    text="抽 1 张牌。",
    rare=Rarity.STANDARD,
    procedures=[
        Procedure(
            EventType.USE,
            lambda card, event, ground: event.dict.get("source") is card,
            action,
        )
    ],
)
```

## 5. 常用卡牌字段

```python
CardData(
    type=CardType.INFANTRY,
    country=Country.SOVIET,
    cost=2,
    display_name="名称",
    text="卡面描述",
    rare=Rarity.STANDARD,
    at=3,
    df=4,
    operation_cost=1,
    art="example.png",
    keywords=[],
    procedures=[],
    tags=[],
)
```

常用类型

```text
INFANTRY
TANK
FIGHTER
BOMBER
ARTILLERY
ORDER
COUNTERMEASURE
```

常用稀有度

```text
STANDARD
LIMITED
SPECIAL
ELITE
```

## 6. Procedure 流程

```python
Procedure(
    trigger,
    condition,
    action,
    target_valid=None,
    any_zone=False,
)
```

- `trigger`: `EventType` 或关键词触发器
- `condition`: 返回 `bool`
- `action`: 实际执行器
- `target_valid`: 指向目标合法性判断
- `any_zone`: 允许在卡组/手牌响应

默认情况下只有场上的卡牌响应事件

例外

- `USE`: 指令在手中时触发
- `LEAVE`: 死亡时卡牌已进入弃牌堆, 仍会触发亡计

如果卡牌明确要在手牌/卡组生效

```python
Procedure(..., any_zone=True)
```

## 7. 常用事件

```text
USE          使用卡牌
ENTER        进入战场
LEAVE        离开战场
DAMAGED      受到伤害
ATTACK       攻击
MOVE         移动
DRAW         抽牌
LOOP         每帧循环
TURN_START   回合开始
TURN_END     回合结束
BUFF         属性增加
CHOICE_RESOLVED 三选一结算
```

## 8. 部署效果

```python
from main import EntryMethod

def deployed(card, event, ground):
    return event.card is card and event.method is EntryMethod.DEPLOY

def action(card, event, ground):
    ground.draw(event.player)

Procedure(EventType.ENTER, deployed, action)
```

## 9. 指向效果

目标合法性写在 `Procedure.target_valid`

```python
def target_valid(target, player, ground):
    return target.is_unit

def action(card, event, ground):
    def apply(target):
        ground.damage(target, 1, DamageType.NONE, card)

    ground.request_target(
        event.player,
        card,
        lambda target: target_valid(target, event.player, ground),
        apply,
    )

Procedure(
    EventType.USE,
    lambda card, event, ground: event.dict.get("source") is card,
    action,
    target_valid=target_valid,
)
```

## 10. 光环效果

LOOP 前会清除上一帧光环, 然后由流程重新施加

```python
def aura(card, event, ground):
    if card.controller is None:
        return
    for line in (
        ground.support_lines[Player.A],
        ground.support_lines[Player.B],
        ground.front_line,
    ):
        for unit in line.units:
            if unit is not card and unit.controller is card.controller:
                ground.add_aura(unit, at=1, source=card)

Procedure(EventType.LOOP, lambda card, event, ground: True, aura)
```

`ground.add_aura` 会

- 增加临时攻击力
- 记录光环来源
- 首次生效时广播 `BUFF`

## 11. 亡计

```python
from mods.kards.code.keywords.destruction import (
    KEYWORD as DESTRUCTION,
)

def last_rites(card, event, ground):
    player = card.controller or card.owner
    if player is None:
        return
    ground.draw(player)
    ground.hqs[player].buff(df=card.cost)

CARD_DATA = CardData(
    ...
    keywords=[DESTRUCTION],
    procedures=[
        Procedure(
            "destruction",
            lambda card, event, ground: event.card is card,
            last_rites,
        )
    ],
)
```

## 12. 三选一与开发

开发从当前卡组中的卡牌 id 生成三张额外副本

```python
ground.develop_from_pool(player, source)
```

开发不会移除卡组中的原牌

选项

- 选中牌加入手牌
- 其余进入弃牌区
- 触发 `DEVELOP`

## 13. 常用 BattleGround 方法

```python
ground.draw(player)
ground.damage(target, amount, damage_type, source)
ground.buff(target, at=1, df=1)
ground.give_card(player, card_id, zone)
ground.return_unit(card, source)
ground.add_unit(player, card)
ground.isolate_card(player, card, source)
ground.request_target(player, source, valid, callback)
ground.start_card_choice(player, cards, Zone.HAND, ...)
ground.shuffle_deck(player)
ground.schedule_action(delay_ms, callback)
```

## 14. 替换其他 Mod 的元素

在 Mod 根目录创建 `replace.json`

```json
{
  "cards/Germany/card_a": "kards/card_b",
  "keywords/my_keyword": "kards/intel"
}
```

路径支持

```text
cards/Germany/card_a
code/cards/Germany/card_a.py
modA/cards/Germany/card_a
modA/code/cards/Germany/card_a.py
modA:card_a
keywords/example
```

替换在全部 Mod 加载完成后执行

## 15. 中文名与资源

`data/zh.json` 用于补充中文名和卡图映射

卡图放在

```text
assets/cards/{Country}/{file}.png
```

关键词图标放在

```text
assets/keyword/{keyword_id}.png
```

## 16. 开发约定

- 使用严格类型注解
- 不要使用全角符号
- 文档和注释使用中文
- 不要随意修改 `main.py` 中的公共流程
- 新机制优先做成关键词或 Procedure
- 指向效果不要直接检查 UI 状态, 用 `target_valid`
- 默认按场上卡牌处理, 手牌/卡组效果显式使用 `any_zone=True`
- 不要重复调用 `card.update`
- 所有伤害通过 `ground.damage` 统一广播

## 17. 本地测试

```powershell
cd D:\Files\Projects\KardsLike\code\v0.1
python main.py
```

仅编译检查

```powershell
python -m py_compile main.py
python -m py_compile mods\my_mod\code\cards\Germany\card_example.py
```

开发完成后提交时不要包含

```text
.venv/
.build/
logs/
crashes/
saves/
完整 mods/kards/assets/
```
