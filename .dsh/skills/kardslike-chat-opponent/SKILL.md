---
name: kardslike-chat-opponent
description: 在不调用外部 API 的情况下，通过文件桥读取 KardsLike 的对局状态，并以对话回合代为完成 AI 出牌或结束回合。
---

# KardsLike 对话对手

当用户要求“替 AI 出牌”“看一下当前 AI 状态”“用对话和我打牌”时使用本技能。

## 前提

玩家已用以下方式启动游戏：

```powershell
$env:KARDSLIKE_CHAT_AI = "1"
python kardslike/main.py
```

轮到 AI 时，游戏会暂停，并写入：

```text
kardslike/chat_ai/state.json
```

然后等待：

```text
kardslike/chat_ai/action.json
```

等待上限为 300 秒，超时后 AI 自动结束回合。

## 操作流程

### 1. 读取状态

在工作区根目录运行：

```powershell
python kardslike/chat_bridge.py show
```

返回 JSON，包含：

```text
turn
credits
hq_df / enemy_hq_df
hand：手牌下标、名称、费用、类型、攻击、防御、文本
support：己方支援线
front：前线
enemy_support / enemy_front
```

### 2. 选择动作

只能从 `hand` 中选择一个合法下标。

- 打出手牌：

```powershell
python kardslike/chat_bridge.py play 0
```

- 结束回合：

```powershell
python kardslike/chat_bridge.py end
```

写入后游戏会继续执行。

### 3. 再次交互

游戏每进入一次 AI 行动，都会重新生成 `state.json`。重复：

```text
show -> play/end -> 等待下一次状态
```

## 决策要求

- 不要修改 `state.json`
- 不要直接调用 DeepSeek API
- 只使用 `chat_bridge.py` 的 `play` / `end`
- 指向型卡牌目前由游戏自动选择第一个合法目标
- 若 `credits` 不足或手牌为空，选择 `end`
- 不要对同一个旧状态重复写入动作

## 文件

```text
kardslike/chat_bridge.py
kardslike/chat_ai/state.json
kardslike/chat_ai/action.json
```

`chat_ai/` 是运行期目录，已被 `.gitignore` 忽略。

## API 模式

如果用户希望不经过对话、直接调用 DeepSeek，可改用：

```text
APIKEY.txt
```

那是另一条 `llm_agent.py` 路径，与本技能的文件桥互斥。
