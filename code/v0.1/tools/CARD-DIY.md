# KARDS Card Forge 本地网页

## 启动

双击：

```text
tools/启动卡牌工坊.cmd
```

使用 Windows 自带 PowerShell 启动本地静态网页服务，并优先用 Edge/Chrome 的应用窗口打开。

不需要安装 Python、Node.js，也不需要联网。

## 地址

```text
http://127.0.0.1:8765/KARDS-DIY-GENERATOR/
```

端口被占用时会自动顺延。

## 文件

```text
card_forge_web/KARDS-DIY-GENERATOR/   原版网页、字体、背景和纹理
start_card_forge.ps1                  PowerShell 本地服务器
启动卡牌工坊.cmd                       双击启动入口
```

## 说明

这是 KARDS Card Forge 的本地静态副本，包含原版卡面模板、背景、纸张纹理、字体、国家/类型下拉框、文本编辑和导出功能。

## 从网页导出到游戏

启动器会监听 Edge 默认下载目录中新增的 PNG：

`	ext
card_*choose*.png
`

在网页里导出并命名为：

`	ext
card_a_choose1.png
card_a_choose2.png
card_expanded_choose1.png
card_expanded_choose2.png
card_advanced_choose1.png
card_advanced_choose2.png
`

文件会自动复制到：

`	ext
tools/card_forge_exports/
mods/kards/assets/cards/Soviet/
`
