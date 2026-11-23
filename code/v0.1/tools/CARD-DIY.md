# KARDS DIY · Python 本地版

本地卡牌生成器，不依赖浏览器和 Node.js。

## 运行

```powershell
cd D:\Files\Projects\KardsLike\code\v0.1
python tools\card_diy.py
```

打开编辑窗口后可以填写：

- 标题
- 类型
- 国家
- 费用
- 行动花费
- 攻击 / 防御
- 稀有度
- 扩展包
- 卡牌文本
- 卡图

点击「导出 PNG」即可生成 `500 × 702` 卡面。

## 命令行

```powershell
python tools\card_diy.py `
  --out card.png `
  --title "测试卡" `
  --text "**部署**：抽 1 张牌。" `
  --type infantry `
  --nation Soviet `
  --cost 2 `
  --at 3 `
  --df 4
```

或使用 JSON：

```json
{
  "title": "测试卡",
  "text": "**部署**：抽 1 张牌。\n[b]守护[/b]。",
  "type": "infantry",
  "nation": "Soviet",
  "cost": 2,
  "operation_cost": 1,
  "at": 3,
  "df": 4,
  "rarity": "Standard",
  "set": "Base",
  "art": "path/to/art.png",
  "out": "card.png"
}
```

```powershell
python tools\card_diy.py --json card.json
```

## 加粗语法

不再使用单字母 `B` 表示加粗。支持以下人类可读写法：

```text
**部署**：抽 1 张牌。
[b]守护[/b]。
{b}闪击{/b}
<b>冲击</b>
```

推荐中文文本使用：

```text
**部署**：...
**亡计**：...
```

## 卡图

支持 PNG、JPG、WEBP。

如果选择的是完整 KARDS 卡面，工具会自动裁出中间插画区域；如果是纯插画，则直接铺满插画框。

## 限制

当前版本是独立的 Python 卡面生成器，不是完整复刻 KARDS Card Forge 的 React 编辑器。它保留核心字段、卡图、加粗文本和 PNG 导出，布局为本地实现的 KARDS 风格卡面。


## 完整 Card Forge 网页本地副本

如果只靠 Python 简化模板无法还原背景、纸张纹理和完整外观，可以直接使用本地网页副本：

```powershell
cd D:\Files\Projects\KardsLike\code\v0.1
python tools\card_forge_server.py
```

它会启动：

```text
http://127.0.0.1:8765/KARDS-DIY-GENERATOR/
```

这是 KARDS Card Forge 的静态网页副本，包含原版编辑器、背景、纸张纹理、字体和卡面模板，不再依赖网络。

文件和模板来源：

```text
raederhans/KARDS-DIY-GENERATOR
```

本地副本位于：

```text
tools/card_forge_web/KARDS-DIY-GENERATOR/
```

## 不安装 Python 的启动方式

直接双击：

`	ext
tools/启动卡牌工坊.cmd
`

使用 Windows 自带的 PowerShell 启动本地网页服务，并优先用 Edge/Chrome 的应用窗口打开 KARDS Card Forge。

不需要安装 Python、Node.js 或联网。
