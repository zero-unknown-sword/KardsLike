"""
tools模块

为pygame添加一些便捷的扩展功能
"""
import ctypes
import logging
import os
import traceback
from datetime import datetime
from logging import Logger
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, TypeAlias, Generic, TypeVar

import pygame
from pygame import Surface
from pygame.event import Event
from pygame.font import Font
from pygame.sprite import Sprite

# 颜色类型: RGB 三元组, RGBA 四元组或颜色名称字符串
Color: TypeAlias = tuple[int, int, int] | tuple[int, int, int, int] | str
"""允许传入一些类型作为颜色参数"""

T = TypeVar("T")
NumType = TypeVar("NumType", int, float)
# TODO, float | int

# trace 级别: 数值 5, 比 DEBUG(10) 更细
TRACE = 5
"""TRACE日志级别"""
logging.addLevelName(TRACE, "TRACE")

# 日志与报错目录(与本模块同级)
LOGS_DIR: Path = Path(__file__).resolve().parent / "logs"
CRASHES_DIR: Path = Path(__file__).resolve().parent / "crashes"

# 报错标题分隔线, 15 个等号
SEPARATOR: str = "=" * 15

# 开发者联系方式
DEV_QQ: str = "3095645670"

# 可自行修复的异常类型及建议处理方案
FIXABLE_ADVICE: dict[type[BaseException], str] = {
    FileNotFoundError: "文件缺失, 请检查游戏文件是否完整, 必要时重新安装",
    PermissionError: "权限不足, 请以管理员身份运行, 或关闭占用该文件的程序",
    IsADirectoryError: "路径指向了文件夹而非文件, 请检查配置",
    NotADirectoryError: "路径中某一部分不是文件夹, 请检查配置",
}


class LogManager:
    """日志管理器, 将运行日志输出到 logs 目录"""

    def setup(self) -> Path:
        """
        初始化日志系统, 创建以启动时间命名的日志文件

        Returns:
            日志文件路径
        """
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / f"{datetime.now():%Y-%m-%d_%H-%M}.log"
        logging.setLoggerClass(BetterLogger)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logging.basicConfig(
            level=TRACE,
            handlers=[file_handler, console],
        )
        logging.info(f"日志文件: {log_file}")
        return log_file


class CrashReporter:
    """报错处理器, 捕获未处理异常并生成报错文件"""

    def __call__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        处理未处理异常, 生成报错文件并弹窗

        Args:
            exc_type: 异常类型
            exc_value: 异常实例
            exc_tb: 异常回溯
        """
        CRASHES_DIR.mkdir(parents=True, exist_ok=True)
        crash_file = CRASHES_DIR / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        crash_file.write_text(
            self._build_report(exc_type, exc_value, exc_tb), encoding="utf-8"
        )
        self._show_message(exc_type, exc_value)
        self._open_file_and_folder(crash_file)

    def _build_report(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> str:
        """
        构建报错文件完整内容

        Args:
            exc_type: 异常类型
            exc_value: 异常实例
            exc_tb: 异常回溯

        Returns:
            报错文件内容
        """
        core, advice = self._core_message(exc_type, exc_value)
        stack = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        lines = [
            f"{SEPARATOR}游戏出错{SEPARATOR}",
            "",
            f"时间: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
            f"核心错误: {core}",
            "",
            "堆栈:",
            stack,
        ]
        if advice is not None:
            lines += ["", f"建议处理方案: {advice}"]
        lines += ["", f"请联系开发者, 我的QQ: {DEV_QQ}"]
        return "\n".join(lines)

    def _core_message(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
    ) -> tuple[str, str | None]:
        """
        根据异常类型生成核心错误消息与建议

        Args:
            exc_type: 异常类型
            exc_value: 异常实例

        Returns:
            (核心错误消息, 建议处理方案, 无建议时为 None)
        """
        advice = FIXABLE_ADVICE.get(exc_type)
        if advice is None:
            return "未知", None
        return f"{exc_type.__name__}: {exc_value}", advice

    def _show_message(
        self, exc_type: type[BaseException], exc_value: BaseException
    ) -> None:
        """
        弹出系统错误对话框

        Args:
            exc_type: 异常类型
            exc_value: 异常实例
        """
        core, advice = self._core_message(exc_type, exc_value)
        lines = [f"核心错误: {core}"]
        if advice is not None:
            lines.append(f"建议处理方案: {advice}")
        lines.append(f"请联系开发者, 我的QQ: {DEV_QQ}")
        ctypes.windll.user32.MessageBoxW(None, "\n".join(lines), "KardsLike 游戏出错", 0x10)

    def _open_file_and_folder(self, crash_file: Path) -> None:
        """
        打开报错文件及其所在文件夹

        Args:
            crash_file: 报错文件路径
        """
        try:
            os.startfile(crash_file)
        except OSError:
            pass
        try:
            os.startfile(CRASHES_DIR)
        except OSError:
            pass


class BetterLogger(Logger):
    """更好的日志记录器, 支持 trace 级别"""

    def trace(self, msg: object, *args: Any, **kwargs: Any) -> None:
        """
        输出 trace 级别日志

        Args:
            msg: 日志消息内容
            args: 消息格式化参数
            kwargs: 额外关键字参数
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


# 让之后通过 logging.getLogger 创建的记录器都支持 trace
logging.setLoggerClass(BetterLogger)


class Button(Sprite):
    """按钮对象, 位置由布局系统设置"""

    def __init__(
        self,
        text: str = "",
        width: int = 320,
        height: int = 64,
        on_click: Callable[[], None] | None = None,
        color: Color = (100, 100, 100),
        hover_color: Color = (130, 130, 130),
        text_color: Color = (255, 255, 255),
        font_size: int = 32,
        font: Font | None = None,
    ) -> None:
        """
        初始化按钮对象

        Args:
            text: 按钮显示的文字
            width: 按钮宽度
            height: 按钮高度
            on_click: 点击时触发的回调
            color: 普通状态下的填充颜色
            hover_color: 鼠标悬浮时的填充颜色
            text_color: 文字颜色
            font_size: 文字字号
            font: 渲染文字的字体, 默认用 pygame 内置字体(不支持中文)
        """
        super().__init__()  # 初始化父类 Sprite
        self.rect: pygame.Rect = pygame.Rect(0, 0, width, height)  # 位置由布局设置
        self.text: str = text
        self.on_click: Callable[[], None] | None = on_click
        self.color: Color = color                 # 普通颜色
        self.hover_color: Color = hover_color     # 悬浮时颜色
        self.text_color: Color = text_color
        self.font: Font = font if font is not None else pygame.font.Font(None, font_size)
        self.image: Surface = pygame.Surface(self.rect.size)
        self._render(self.color)           # 生成初始图像

    def _render(self, fill_color: Color) -> None:
        """
        按指定颜色重绘按钮表面

        Args:
            fill_color: 用于填充按钮表面的颜色
        """
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(fill_color)
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            self.image.blit(text_surf, text_surf.get_rect(center=self.image.get_rect().center))

    def is_hovered(self) -> bool:
        """
        判断鼠标当前是否悬浮在按钮上

        Returns:
            鼠标是否悬浮在按钮上
        """
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_clicked(self, event: Event) -> bool:
        """
        判断某次事件是否点击了此按钮

        Args:
            event: pygame 事件, 通常传入 MOUSEBUTTONDOWN 事件

        Returns:
            事件是否为点击此按钮的左键按下事件
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        每帧调用, 根据悬浮状态切换按钮颜色

        Args:
            args: 位置参数
            kwargs: 关键字参数
        """
        self._render(self.hover_color if self.is_hovered() else self.color)


class ButtonGroup:
    """按钮组, 负责自动布局与事件分发"""

    def __init__(self) -> None:
        """创建空按钮组"""
        self.buttons: list[Button] = []

    def add(self, button: Button) -> None:
        """
        添加按钮

        Args:
            button: 按钮
        """
        self.buttons.append(button)

    def layout_vertical(self, center_x: int, start_y: int, gap: int = 24) -> None:
        """
        垂直居中排列所有按钮

        Args:
            center_x: 水平中心坐标
            start_y: 首个按钮的纵坐标
            gap: 按钮间距
        """
        y = start_y
        for button in self.buttons:
            button.rect.centerx = center_x
            button.rect.y = y
            y += button.rect.height + gap

    def handle_event(self, event: Event) -> Button | None:
        """
        处理事件, 触发被点击按钮的回调

        Args:
            event: pygame 事件

        Returns:
            被点击的按钮, 无则返回 None
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        for button in self.buttons:
            if button.rect.collidepoint(event.pos):
                if button.on_click is not None:
                    button.on_click()
                return button
        return None

    def update(self) -> None:
        """更新所有按钮的悬浮状态"""
        for button in self.buttons:
            button.update()

    def draw(self, screen: Surface) -> None:
        """
        绘制所有按钮

        Args:
            screen: 屏幕 Surface
        """
        for button in self.buttons:
            screen.blit(button.image, button.rect)


class ImageLoader:
    """图片资源加载器, 负责加载并缓存 Surface"""

    def __init__(self) -> None:
        """初始化加载器, 创建空缓存"""
        self.caches: dict[Path, Surface] = {}

    def load(self, path: Path) -> Surface:
        """
        加载指定路径的图片, 命中缓存则直接返回

        Args:
            path: 图片文件路径

        Returns:
            加载得到的 Surface
        """
        if path in self.caches:
            return self.caches[path]
        surface = pygame.image.load(path)
        self.caches[path] = surface
        return surface

    def clear(self) -> None:
        """清空缓存"""
        self.caches.clear()

class Attr(Generic[T]):
    """
    Attr

    属性基类, 保存基础值、名称与所有者
    """
    def __init__(self, val: T, name: str = "", owner: object | None = None) -> None:
        """
        初始化属性

        Args:
            val: 基础值
            name: 属性名
            owner: 所属对象
        """
        self._val: T = val
        """基础值"""
        self.name: str = name
        self.owner: object | None = owner
        self.type: type[T] = type(val)

    @property
    def val(self) -> T:
        """当前值"""
        return self._val

    def set(self, val: T) -> None:
        """设置基础值"""
        self._val = val


class NumAttr(Attr[NumType], Generic[NumType]):
    """数值属性, 由基础值与临时值组成"""
    def __init__(
        self,
        val: NumType,
        name: str = "",
        owner: object | None = None,
    ) -> None:
        super().__init__(val, name, owner)
        self.temp: NumType = 0  # type: ignore[assignment]
        """临时值"""

    def set_temp(self, temp: NumType) -> None:
        """设置临时值"""
        self.temp = temp

    def reset_temp(self) -> None:
        """清除临时值"""
        self.temp = 0  # type: ignore[assignment]

    @property
    def val(self) -> NumType:
        """当前值 = 基础值 + 临时值"""
        return self.temp + self._val


class IntAttr(NumAttr[int]):
    """整数属性, 默认上限 99"""
    def __init__(
        self,
        val: int = 0,
        name: str = "",
        owner: object | None = None,
        max_value: int = 99,
    ) -> None:
        self.max_value = max_value
        super().__init__(min(max(val, 0), max_value), name, owner)

    def set(self, val: int) -> None:
        """设置基础值并限制范围"""
        self._val = min(max(val, 0), self.max_value)

    @property
    def val(self) -> int:
        return min(max(self.temp + self._val, 0), self.max_value)

    def __int__(self) -> int:
        return int(self.val)

    def __index__(self) -> int:
        return int(self.val)

    def __str__(self) -> str:
        return str(self.val)

    def __repr__(self) -> str:
        return f"IntAttr({self.val})"

    def __eq__(self, other: object) -> bool:
        return self.val == other

    def __lt__(self, other: int) -> bool:
        return self.val < other

    def __le__(self, other: int) -> bool:
        return self.val <= other

    def __gt__(self, other: int) -> bool:
        return self.val > other

    def __ge__(self, other: int) -> bool:
        return self.val >= other

    def __add__(self, other: int) -> int:
        return self.val + other

    def __radd__(self, other: int) -> int:
        return other + self.val

    def __sub__(self, other: int) -> int:
        return self.val - other

    def __rsub__(self, other: int) -> int:
        return other - self.val

    def __mul__(self, other: int) -> int:
        return self.val * other

    def __rmul__(self, other: int) -> int:
        return other * self.val
