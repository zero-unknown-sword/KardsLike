"""文件桥：让对话 AI 在游戏外决定出牌。

游戏 AI 回合会暂停并把状态写入 chat_ai/state.json；
外部通过命令行写入 chat_ai/action.json，游戏读取后继续。
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from main import BattleGround, Card, Player

STATE_DIR = Path(__file__).resolve().parent / "chat_ai"
STATE_FILE = STATE_DIR / "state.json"
ACTION_FILE = STATE_DIR / "action.json"


def _unit_data(unit: "Card", index: int) -> dict[str, Any]:
    return {
        "index": index,
        "name": unit.display_name or unit.name,
        "cost": unit.cost,
        "at": unit.at,
        "df": unit.df,
        "type": unit.type.name.lower(),
        "text": unit.text,
    }


def publish_state(ground: "BattleGround", player: "Player") -> Path:
    """把当前 AI 回合状态写入 state.json。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    support = ground.support_lines[player]
    front = ground.front_line
    enemy = player.opponent
    state = {
        "turn": ground.turn_count,
        "player": player.name,
        "credits": ground.kredits[player].credits,
        "hq_df": ground.hqs[player].df,
        "enemy_hq_df": ground.hqs[enemy].df,
        "hand": [
            {
                "index": index,
                "name": card.display_name or card.name,
                "cost": card.cost,
                "type": card.type.name.lower(),
                "at": card.at,
                "df": card.df,
                "text": card.text,
                "targeted": card.targeted,
            }
            for index, card in enumerate(ground.hands[player].cards)
        ],
        "support": [_unit_data(unit, index) for index, unit in enumerate(support.units)],
        "front": {
            "owner": front.owner.name if front.owner else None,
            "units": [_unit_data(unit, index) for index, unit in enumerate(front.units)],
        },
        "enemy_support": [
            _unit_data(unit, index) for index, unit in enumerate(ground.support_lines[enemy].units)
        ],
        "enemy_front": {
            "owner": front.owner.name if front.owner else None,
            "units": [_unit_data(unit, index) for index, unit in enumerate(front.units)],
        },
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    ACTION_FILE.unlink(missing_ok=True)
    return STATE_FILE


def wait_action(timeout: float = 300.0) -> dict[str, Any] | None:
    """等待外部写入 action.json。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ACTION_FILE.is_file():
            try:
                raw = json.loads(ACTION_FILE.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                time.sleep(0.2)
                continue
            if isinstance(raw, dict):
                ACTION_FILE.unlink(missing_ok=True)
                return raw
        time.sleep(0.2)
    return None


def write_action(action: dict[str, Any]) -> None:
    """写入一次动作。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ACTION_FILE.write_text(json.dumps(action, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    """命令行: show / play N / end / clear。"""
    import argparse

    parser = argparse.ArgumentParser(description="KardsLike 对话 AI 桥")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", help="打印当前状态")
    play = sub.add_parser("play", help="打出手牌")
    play.add_argument("index", type=int)
    attack = sub.add_parser("attack", help="用支援线单位攻击")
    attack.add_argument("attacker", type=int)
    attack.add_argument("target", help="hq 或 support/front")
    attack.add_argument("target_index", type=int, nargs="?")
    sub.add_parser("end", help="结束回合")
    sub.add_parser("clear", help="清除动作")
    args = parser.parse_args()
    if args.command == "show":
        print(STATE_FILE.read_text(encoding="utf-8") if STATE_FILE.is_file() else "{}")
    elif args.command == "play":
        write_action({"type": "play", "index": args.index})
        print(f"queued play {args.index}")
    elif args.command == "attack":
        action = {"type": "attack", "attacker": args.attacker, "target": args.target}
        if args.target_index is not None:
            action["target_index"] = args.target_index
        write_action(action)
        print(f"queued attack {args.attacker} -> {args.target}")
    elif args.command == "end":
        write_action({"type": "end"})
        print("queued end")
    elif args.command == "clear":
        ACTION_FILE.unlink(missing_ok=True)
        print("cleared")


if __name__ == "__main__":
    main()
