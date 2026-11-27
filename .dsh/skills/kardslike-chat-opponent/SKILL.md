---
name: kardslike-chat-opponent
description: 用当前 DSH 会话直接陪用户打 KardsLike。通过 wait_turn 阻塞到 AI 回合，再 send_action 出牌/攻击/结束，循环直到游戏结束，不需要用户每条消息提醒。
---

# KardsLike 当前会话对手

当用户说“开打”“用当前会话打”“陪我打一局”时使用本技能。

目标：**在一次对话回合内完成一整局**，不需要用户反复说“到你了”。

## 前提

游戏必须用文件桥模式启动：

```powershell
$env:KARDSLIKE_CHAT_AI = "1"
.\.venv\Scripts\python.exe kardslike\main.py
```

用户只需要在游戏里点一次“开始”。

## 两个工具

### 读取：等待 AI 回合

```powershell
.\.venv\Scripts\python.exe kardslike\tools\wait_turn.py --timeout 300
```

行为：

- 玩家回合：阻塞不返回
- 轮到 AI：返回当前完整 `state.json`
- 游戏结束：返回 `GAME_OVER winner=...`
- 超时：返回 `WAIT_TIMEOUT`

### 输出：发送动作

```powershell
.\.venv\Scripts\python.exe kardslike\tools\send_action.py play 0
.\.venv\Scripts\python.exe kardslike\tools\send_action.py attack 0 hq
.\.venv\Scripts\python.exe kardslike\tools\send_action.py attack 0 front 0
.\.venv\Scripts\python.exe kardslike\tools\send_action.py attack 0 support 0
.\.venv\Scripts\python.exe kardslike\tools\send_action.py end
```

如果返回：

```text
NOT_AI_TURN
```

说明动作发送太晚，AI 回合已结束。不要重发旧动作，直接重新 `wait_turn`。

## 一局循环

```text
1. wait_turn
2. 读状态，选择合法动作
3. send_action
4. 如果游戏结束，停止
5. 否则回到 1
```

连续调用工具，直到：

```text
GAME_OVER
```

不要每出一张牌就回复用户；打完或遇到异常再总结。

## 决策规则

- 优先斩杀：能打总部的空军/炮兵先算总伤害，达到敌方 HQ DF 就优先打脸
- 支援线满 4 个单位时不要再出单位，改用指令或攻击
- 步兵/坦克只有在前线才能打总部；支援线地面单位打不到总部
- 守护会挡总部；有守护时优先解守护
- 烟幕单位不能被普通攻击选中
- 闪击单位当回合可以行动
- 不要用低攻单位白送高攻目标；没有好交换就结束回合
- 能清场、抽牌、保护总部时优先做

## 攻击目标格式

```text
hq             敌方总部
front N        敌方前线第 N 个单位
support N      敌方支援线第 N 个单位
```

前线单位攻击时加：

```text
--line front
```

例如：

```powershell
send_action.py attack 0 front 1 --line front
```

## 异常处理

- `WAIT_TIMEOUT`：游戏可能已退出或没有开始战斗，检查窗口
- `NOT_AI_TURN`：重新等待，不要重复写动作
- `action.json` 残留：不要手动删除，下一次 publish_state 会清理
- 游戏窗口关闭：停止调用工具，总结对局结束

## 不要使用

- 不要启动 `auto_player.py`，那会与本技能的当前会话决策冲突
- 不要每个动作都向用户请示
- 不要在用户回合写动作
