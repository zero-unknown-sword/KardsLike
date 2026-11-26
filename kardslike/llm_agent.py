"""DeepSeek 对手策略。

使用 OpenAI 兼容接口，每回合只让模型选择一张手牌。
攻击、移动和结束回合仍由本地 AIController 负责。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from main import BattleGround, Card, Player

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - 未安装时退回本地 AI
    OpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger("kardslike.llm")

API_KEY_FILES = (
    Path(__file__).resolve().parent / "APIKEY.txt",
    Path(__file__).resolve().parent.parent / "APIKEY.txt",
)
"""API Key 文件查找位置"""

MODEL = "deepseek-chat"
"""默认模型"""


def _read_api_key() -> str:
    """读取 APIKEY.txt，支持纯 key 或 DEEPSEEK_API_KEY=..."""
    for path in API_KEY_FILES:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                text = line.strip()
                if not text or text.startswith("#"):
                    continue
                if "=" in text:
                    key_name, value = text.split("=", 1)
                    if key_name.strip().upper() in {"DEEPSEEK_API_KEY", "API_KEY", "OPENAI_API_KEY"}:
                        return value.strip().strip('"').strip("'")
                elif text.startswith("sk-"):
                    return text
        except OSError:
            continue
    return ""


class DeepSeekPlanner:
    """让 DeepSeek 选择当前回合要打出的牌。"""

    def __init__(self) -> None:
        self.api_key = _read_api_key()
        self.client: Any = None
        if self.api_key and OpenAI is not None:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com",
                    timeout=12.0,
                    max_retries=0,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("DeepSeek 客户端初始化失败: %s", exc)
                self.client = None

    @property
    def available(self) -> bool:
        return self.client is not None

    def choose_card(
        self,
        ground: "BattleGround",
        player: "Player",
        cards: list["Card"],
    ) -> int | None:
        """返回要打出的手牌下标；-1 表示本回合不再出牌。"""
        if self.client is None or not cards:
            return None
        enemy = player.opponent
        support = ground.support_lines[player]
        enemy_units = [
            f"{unit.display_name}({unit.at}/{unit.df})" for unit in support.units
        ]
        front = ground.front_line
        front_text = "无" if front.owner is None else (
            f"{front.owner} " + ", ".join(f"{u.display_name}({u.at}/{u.df})" for u in front.units)
        )
        hand_lines = [
            f"{index}: {card.display_name} 费用{card.cost} "
            f"{'单位' if card.is_unit else '指令'} "
            f"{card.at}/{card.df} {card.text[:80]}"
            for index, card in enumerate(cards)
        ]
        prompt = f"""你是 KARDS 玩家。当前是第 {ground.turn_count} 回合，你控制 {player.name}。
指挥点：{ground.kredits[player].credits}
总部防御：{ground.hqs[player].df}，敌方总部：{ground.hqs[enemy].df}
己方支援线：{', '.join(enemy_units) or '空'}
前线：{front_text}
敌方场面：{', '.join(f'{u.display_name}({u.at}/{u.df})' for u in ground.all_targets() if u.controller is enemy) or '空'}

可打出的手牌（下标: 名称）：
{chr(10).join(hand_lines)}

只输出 JSON，不要解释：{{"choice": 下标或 -1, "reason": "不超过20字"}}
-1 表示本回合不再出牌。优先考虑站场、解场和斩杀。"""
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "你只输出合法 JSON。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=80,
            )
            content = response.choices[0].message.content or ""
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                payload = json.loads(content[start : end + 1])
                choice = int(payload.get("choice", -1))
                if -1 <= choice < len(cards):
                    logger.info("DeepSeek 选择手牌 %s", choice)
                    return choice
        except Exception as exc:
            logger.warning("DeepSeek 决策失败，回退本地 AI: %s", exc)
        return None
