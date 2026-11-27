"""向正在等待的 AI 回合发送一个动作。

用法:
    python kardslike/tools/send_action.py play 0
    python kardslike/tools/send_action.py attack 0 hq
    python kardslike/tools/send_action.py attack 0 front 0
    python kardslike/tools/send_action.py attack 0 support 1 --line front
    python kardslike/tools/send_action.py end
    python kardslike/tools/send_action.py json '{"type":"end"}'
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHAT_DIR = ROOT / "kardslike" / "chat_ai"
LIVE_FILE = CHAT_DIR / "live.json"
ACTION_FILE = CHAT_DIR / "action.json"


def write_action(action: dict[str, Any]) -> None:
    ACTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(action, ensure_ascii=False, indent=2)
    last: Exception | None = None
    for _ in range(10):
        try:
            ACTION_FILE.write_text(payload, encoding="utf-8")
            return
        except PermissionError as exc:
            last = exc
            time.sleep(0.05)
    if last is not None:
        raise last


def ai_ready() -> bool:
    try:
        live = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(live.get("waiting") and live.get("ready") and live.get("owner") == "B")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    play = sub.add_parser("play")
    play.add_argument("index", type=int)
    attack = sub.add_parser("attack")
    attack.add_argument("attacker", type=int)
    attack.add_argument("target", choices=("hq", "support", "front"))
    attack.add_argument("target_index", type=int, nargs="?")
    attack.add_argument("--line", choices=("support", "front"), default="support")
    sub.add_parser("end")
    json_cmd = sub.add_parser("json")
    json_cmd.add_argument("payload")
    args = parser.parse_args()

    if not ai_ready():
        print("NOT_AI_TURN")
        return 2

    if args.command == "play":
        action: dict[str, Any] = {"type": "play", "index": args.index}
    elif args.command == "attack":
        action = {
            "type": "attack",
            "attacker": args.attacker,
            "attacker_line": args.line,
            "target": args.target,
        }
        if args.target_index is not None:
            action["target_index"] = args.target_index
    elif args.command == "end":
        action = {"type": "end"}
    else:
        try:
            action = json.loads(args.payload)
        except ValueError as exc:
            print(f"BAD_JSON {exc}")
            return 2
        if not isinstance(action, dict):
            print("BAD_JSON")
            return 2
    write_action(action)
    print(f"QUEUED {json.dumps(action, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
