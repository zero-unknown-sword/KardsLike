"""KARDS 风格卡牌 DIY 工具（Python 本地版）

用法：
    python card_diy.py                         # 打开编辑窗口
    python card_diy.py --json card.json        # 从 JSON 生成
    python card_diy.py --out card.png --title "测试卡" --text "**部署**：抽 1 张牌。"

文字加粗使用人类可读的标记，不再用单字母 B：
    **加粗**        [b]加粗[/b]        {b}加粗{/b}        <b>加粗</b>

卡牌 JSON 字段：
    title, text, type, nation, cost, operation_cost, at, df,
    rarity, set, art, out
"""
from __future__ import annotations

import argparse
import json
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageTk

# cSpell:ignore msyh msyhbd textbbox textlength LANCZOS vdraw pady textvariable columnspan initialfile
CARD_W = 500
CARD_H = 702
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
BOLD_FONT = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FALLBACK_FONT = Path(r"C:\Windows\Fonts\simhei.ttf")

PAPER = (216, 210, 189)
INK = (55, 55, 48)
MUTED = (104, 101, 88)
DARK = (63, 66, 59)
GOLD = (186, 151, 70)
LIGHT = (245, 241, 226)
RED = (126, 47, 42)
GREEN = (68, 91, 60)

TYPE_NAMES = {
    "infantry": "步兵",
    "tank": "坦克",
    "artillery": "炮兵",
    "fighter": "战斗机",
    "bomber": "轰炸机",
    "order": "指令",
    "countermeasure": "反制",
}


@dataclass
class CardSpec:
    """一张 DIY 卡的输入数据。"""

    title: str = "未命名卡牌"
    text: str = ""
    type: str = "infantry"
    nation: str = "Soviet"
    cost: int = 1
    operation_cost: int = 1
    at: int = 1
    df: int = 1
    rarity: str = "Standard"
    set_name: str = "Base"
    art: str = ""
    out: str = "card.png"


@dataclass
class Segment:
    """一段带加粗状态的行内文字。"""

    text: str
    bold: bool = False


@dataclass
class Line:
    """排版后的一行。"""

    segments: list[Segment] = field(default_factory=lambda: list[Segment]())
    width: int = 0


FontType = ImageFont.FreeTypeFont | ImageFont.ImageFont


def _font(path: Path, size: int) -> FontType:
    """加载字体，找不到时回退到系统黑体。"""
    for item in (path, DEFAULT_FONT, FALLBACK_FONT):
        if item.is_file():
            try:
                return ImageFont.truetype(str(item), size)
            except OSError:
                continue
    return ImageFont.load_default()


def parse_markup(text: str) -> list[Segment]:
    """
    解析加粗标记。

    支持 **粗体**、[b]粗体[/b]、{b}粗体{/b}、<b>粗体</b>。
    单字母 B 不再作为加粗标记。
    """
    patterns = [
        ("**", "**"),
        ("[b]", "[/b]"),
        ("[B]", "[/B]"),
        ("{b}", "{/b}"),
        ("<b>", "</b>"),
    ]
    segments: list[Segment] = []
    index = 0
    while index < len(text):
        best: tuple[int, str, str] | None = None
        for opening, closing in patterns:
            found = text.find(opening, index)
            if found != -1 and (best is None or found < best[0]):
                end = text.find(closing, found + len(opening))
                if end != -1:
                    best = (found, opening, closing)
        if best is None:
            segments.append(Segment(text[index:]))
            break
        start, opening, closing = best
        if start > index:
            segments.append(Segment(text[index:start]))
        content_start = start + len(opening)
        content_end = text.find(closing, content_start)
        segments.append(Segment(text[content_start:content_end], bold=True))
        index = content_end + len(closing)
    return [item for item in segments if item.text]


def _text_width(draw: ImageDraw.ImageDraw, segment: Segment, font: FontType) -> int:
    """测量一段文字宽度。"""
    box = draw.textbbox((0, 0), segment.text, font=font)
    return int(box[2] - box[0])


def wrap_segments(
    draw: ImageDraw.ImageDraw,
    segments: Iterable[Segment],
    font_regular: FontType,
    font_bold: FontType,
    max_width: int,
) -> list[Line]:
    """按像素宽度换行，同时保留加粗片段。"""
    chars: list[tuple[str, bool]] = []
    for segment in segments:
        for char in segment.text:
            chars.append((char, segment.bold))

    lines: list[Line] = []
    current: list[tuple[str, bool]] = []
    width = 0

    def flush() -> None:
        nonlocal current, width
        if not current:
            return
        line_chars = current[:]
        while line_chars and line_chars[0][0] == " ":
            line_chars.pop(0)
        line = Line()
        for char, bold in line_chars:
            if line.segments and line.segments[-1].bold == bold:
                line.segments[-1].text += char
            else:
                line.segments.append(Segment(char, bold))
        line.width = int(sum(
            draw.textlength(part.text, font=font_bold if part.bold else font_regular)
            for part in line.segments
        ))
        lines.append(line)
        current = []
        width = 0

    for char, bold in chars:
        if char == "\n":
            flush()
            continue
        font = font_bold if bold else font_regular
        char_width = int(draw.textlength(char, font=font))
        if current and width + char_width > max_width:
            flush()
        current.append((char, bold))
        width += char_width
    flush()
    return lines


def draw_segments(
    draw: ImageDraw.ImageDraw,
    lines: list[Line],
    x: int,
    y: int,
    line_height: int,
    font_regular: FontType,
    font_bold: FontType,
    fill: tuple[int, int, int] = INK,
    center_width: int | None = None,
) -> int:
    """绘制已排版的行，返回下一行 y。"""
    for line in lines:
        cursor = x
        if center_width is not None:
            cursor = x + (center_width - line.width) // 2
        for segment in line.segments:
            font = font_bold if segment.bold else font_regular
            draw.text((cursor, y), segment.text, font=font, fill=fill)
            cursor += _text_width(draw, segment, font)
        y += line_height
    return y


def _rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int] | None,
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    """绘制圆角矩形。"""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _load_art(path: Path) -> Image.Image | None:
    """载入卡图；若传入整张卡牌图，则自动裁出插画区域。"""
    try:
        art = Image.open(path).convert("RGB")
    except OSError:
        return None
    ratio = art.width / max(1, art.height)
    if art.width >= 350 and abs(ratio - CARD_W / CARD_H) < 0.08:
        left = int(art.width * 0.056)
        top = int(art.height * 0.16)
        right = int(art.width * 0.944)
        bottom = int(art.height * 0.68)
        art = art.crop((left, top, right, bottom))
    return art


def _fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """等比裁剪填满目标区域。"""
    target_w, target_h = size
    ratio = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (max(1, int(image.width * ratio)), max(1, int(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _paper_texture() -> Image.Image:
    """生成轻微纸张纹理。"""
    image = Image.new("RGB", (CARD_W, CARD_H), PAPER)
    noise = Image.effect_noise((CARD_W, CARD_H), 12).convert("L")
    overlay = Image.new("RGB", (CARD_W, CARD_H), (196, 190, 171))
    return Image.composite(overlay, image, noise)


def render_card(spec: CardSpec) -> Image.Image:
    """根据输入数据生成一张 KARDS 风格卡面。"""
    image = _paper_texture().convert("RGBA")
    draw = ImageDraw.Draw(image)
    title_font = _font(BOLD_FONT, 38)
    body_regular = _font(DEFAULT_FONT, 26)
    body_bold = _font(BOLD_FONT, 26)
    small = _font(DEFAULT_FONT, 18)
    cost_font = _font(BOLD_FONT, 54)
    stat_font = _font(BOLD_FONT, 40)

    # 卡框
    _rounded(draw, (6, 6, CARD_W - 6, CARD_H - 6), 22, None, (96, 89, 72), 4)
    _rounded(draw, (13, 13, CARD_W - 13, CARD_H - 13), 17, None, (236, 230, 208), 2)

    # 顶部费用牌
    _rounded(draw, (22, 20, 96, 100), 10, (54, 57, 52), (24, 26, 23), 2)
    draw.text((59, 60), str(max(0, spec.cost)), font=cost_font, fill=LIGHT, anchor="mm")

    # 右上角类型/阵营
    kind_name = TYPE_NAMES.get(spec.type, spec.type)
    draw.text((CARD_W - 34, 32), kind_name, font=small, fill=MUTED, anchor="ra")
    draw.text((CARD_W - 34, 56), spec.nation, font=small, fill=MUTED, anchor="ra")
    _rounded(
        draw,
        (CARD_W - 108, 78, CARD_W - 34, 96),
        8,
        (231, 225, 203),
        (145, 137, 116),
        1,
    )
    draw.text((CARD_W - 71, 87), spec.rarity, font=_font(DEFAULT_FONT, 12), fill=INK, anchor="mm")

    # 插画区域
    art_box = (28, 112, CARD_W - 28, 470)
    _rounded(draw, art_box, 6, (62, 66, 55), (40, 42, 35), 3)
    if spec.art:
        art = _load_art(Path(spec.art))
        if art is not None:
            art = _fit_cover(art, (art_box[2] - art_box[0] - 8, art_box[3] - art_box[1] - 8))
            image.paste(art, (art_box[0] + 4, art_box[1] + 4))
    # 插画暗角
    vignette = Image.new("L", (CARD_W, CARD_H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle(art_box, fill=0)
    for offset in range(40):
        alpha = int(80 * (1 - offset / 40))
        vdraw.rectangle(
            (art_box[0] + offset, art_box[1] + offset, art_box[2] - offset, art_box[3] - offset),
            outline=alpha,
            width=1,
        )
    image = Image.composite(Image.new("RGBA", image.size, (0, 0, 0, 80)), image, vignette)
    draw = ImageDraw.Draw(image)

    # 标题
    title = spec.title.strip() or "未命名卡牌"
    title_font = _font(BOLD_FONT, 34)
    while draw.textlength(title, font=title_font) > CARD_W - 80 and len(title) > 1:
        title = title[:-1]
    draw.text((CARD_W // 2, 482), title, font=title_font, fill=INK, anchor="ma")

    # 正文
    body_box = (44, 536, CARD_W - 44, 642)
    _rounded(draw, (30, 528, CARD_W - 30, 646), 10, (229, 222, 200), (170, 161, 138), 1)
    segments = parse_markup(spec.text)
    lines = wrap_segments(draw, segments, body_regular, body_bold, body_box[2] - body_box[0])
    max_lines = 4
    lines = lines[:max_lines]
    draw_segments(
        draw,
        lines,
        body_box[0],
        body_box[1],
        26,
        body_regular,
        body_bold,
        fill=INK,
        center_width=body_box[2] - body_box[0],
    )

    # 底部单位数值
    if spec.type not in ("order", "countermeasure"):
        _rounded(draw, (26, 654, 116, 692), 10, (74, 68, 54), (38, 37, 30), 2)
        draw.text((40, 674), "AT", font=small, fill=LIGHT, anchor="lm")
        draw.text((100, 674), str(max(0, spec.at)), font=stat_font, fill=LIGHT, anchor="rm")
        _rounded(draw, (CARD_W - 116, 654, CARD_W - 26, 692), 10, (88, 49, 42), (42, 27, 24), 2)
        draw.text((CARD_W - 100, 674), "DF", font=small, fill=LIGHT, anchor="lm")
        draw.text((CARD_W - 40, 674), str(max(0, spec.df)), font=stat_font, fill=LIGHT, anchor="rm")
        draw.text((CARD_W // 2, 674), f"OC {max(0, spec.operation_cost)}", font=small, fill=MUTED, anchor="mm")

    draw.text(
        (CARD_W // 2, 690),
        f"{spec.set_name}  ·  KARDS DIY",
        font=_font(DEFAULT_FONT, 12),
        fill=(145, 137, 116),
        anchor="mm",
    )
    return image.convert("RGB")


class CardDiyApp:
    """简单的本地卡牌编辑窗口。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("KARDS DIY · Python")
        self.art_path = ""
        self.preview: ImageTk.PhotoImage | None = None

        self.vars: dict[str, tk.StringVar] = {
            "title": tk.StringVar(value="测试卡"),
            "text": tk.StringVar(value="**部署**：抽 1 张牌。"),
            "type": tk.StringVar(value="infantry"),
            "nation": tk.StringVar(value="Soviet"),
            "cost": tk.StringVar(value="1"),
            "oc": tk.StringVar(value="1"),
            "at": tk.StringVar(value="1"),
            "df": tk.StringVar(value="1"),
            "rarity": tk.StringVar(value="Standard"),
            "set": tk.StringVar(value="Base"),
        }
        self._build()
        self.refresh()

    def _build(self) -> None:
        """创建界面。"""
        left = ttk.Frame(self.root, padding=10)
        left.grid(row=0, column=0, sticky="ns")
        right = ttk.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        row = 0
        for label, key in [
            ("标题", "title"),
            ("类型", "type"),
            ("国家", "nation"),
            ("费用", "cost"),
            ("行动花费", "oc"),
            ("攻击", "at"),
            ("防御", "df"),
            ("稀有度", "rarity"),
            ("扩展包", "set"),
        ]:
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(left, textvariable=self.vars[key], width=28).grid(row=row, column=1, pady=2)
            row += 1

        ttk.Label(left, text="卡牌文本").grid(row=row, column=0, sticky="nw", pady=2)
        text = tk.Text(left, width=32, height=8, wrap="word")
        text.insert("1.0", self.vars["text"].get())
        text.grid(row=row, column=1, pady=2)
        self.text_widget = text
        row += 1

        ttk.Button(left, text="选择卡图", command=self.choose_art).grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)
        row += 1
        ttk.Button(left, text="生成预览", command=self.refresh).grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)
        row += 1
        ttk.Button(left, text="导出 PNG", command=self.export).grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)

        self.preview_label = ttk.Label(right)
        self.preview_label.pack(fill="both", expand=True)

    def spec(self) -> CardSpec:
        """从界面读取卡牌数据。"""
        data = {key: var.get() for key, var in self.vars.items()}
        self.vars["text"].set(self.text_widget.get("1.0", "end").strip())
        data["text"] = self.vars["text"].get()

        def number(key: str) -> int:
            try:
                return max(0, int(data.get(key, "0")))
            except ValueError:
                return 0

        return CardSpec(
            title=data["title"],
            text=data["text"],
            type=data["type"] or "infantry",
            nation=data["nation"] or "Soviet",
            cost=number("cost"),
            operation_cost=number("oc"),
            at=number("at"),
            df=number("df"),
            rarity=data["rarity"] or "Standard",
            set_name=data["set"] or "Base",
            art=self.art_path,
        )

    def refresh(self) -> None:
        """刷新预览。"""
        image = render_card(self.spec())
        preview = image.copy()
        preview.thumbnail((500, 702))
        self.preview = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.preview)

    def choose_art(self) -> None:
        """选择卡图。"""
        path = filedialog.askopenfilename(
            title="选择卡图",
            filetypes=[("图片", "*.png *.jpg *.jpeg *.webp"), ("全部文件", "*.*")],
        )
        if path:
            self.art_path = path
            self.refresh()

    def export(self) -> None:
        """导出 PNG。"""
        path = filedialog.asksaveasfilename(
            title="导出卡牌",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile="card.png",
        )
        if path:
            render_card(self.spec()).save(path)
            messagebox.showinfo("完成", f"已导出：\n{path}")


def load_spec(path: Path) -> CardSpec:
    """从 JSON 读取卡牌。"""
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    fields = {field.name for field in CardSpec.__dataclass_fields__.values()}
    return CardSpec(**{key: value for key, value in data.items() if key in fields})


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="KARDS 风格卡牌 DIY 工具")
    parser.add_argument("--json", type=Path, help="卡牌 JSON")
    parser.add_argument("--out", help="输出 PNG")
    parser.add_argument("--title", help="卡牌标题")
    parser.add_argument("--text", help="卡牌文本")
    parser.add_argument("--type", default="infantry")
    parser.add_argument("--nation", default="Soviet")
    parser.add_argument("--cost", type=int, default=1)
    parser.add_argument("--oc", type=int, default=1)
    parser.add_argument("--at", type=int, default=1)
    parser.add_argument("--df", type=int, default=1)
    parser.add_argument("--art", default="")
    args = parser.parse_args()

    if args.json:
        spec = load_spec(args.json)
    elif args.title is not None or args.text is not None:
        spec = CardSpec(
            title=args.title or "未命名卡牌",
            text=args.text or "",
            type=args.type,
            nation=args.nation,
            cost=args.cost,
            operation_cost=args.oc,
            at=args.at,
            df=args.df,
            art=args.art,
        )
    else:
        root = tk.Tk()
        CardDiyApp(root)
        root.mainloop()
        return

    if args.out:
        spec.out = args.out
    image = render_card(spec)
    image.save(spec.out)
    print(f"已生成: {Path(spec.out).resolve()}")


if __name__ == "__main__":
    main()
