"""等待 AI 回合开始，并输出当前状态。

用法:
    python kardslike/tools/wait_turn.py
    python kardslike/tools/wait_turn.py --timeout 600
    python kardslike/tools/wait_turn.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAT_DIR = ROOT / "kardslike" / "chat_ai"
LIVE_FILE = CHAT_DIR / "live.json"
STATE_FILE = CHAT_DIR / "state.json"
ACTION_FILE = CHAT_DIR / "action.json"


def read_json(path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return raw if isinstance(raw, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--json", action="store_true", help="只输出状态 JSON")
    args = parser.parse_args()
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        live = read_json(LIVE_FILE)
        winner = live.get("winner")
        if winner:
            print(f"GAME_OVER winner={winner}")
            return 0
        if ACTION_FILE.exists():
            time.sleep(0.1)
            continue
        if live.get("waiting") and live.get("ready") and str(live.get("owner")) == "B":
            state = read_json(STATE_FILE)
            if state and str(state.get("turn")) == str(live.get("turn")):
                print(json.dumps(state, ensure_ascii=False, indent=2))
                return 0
        time.sleep(0.25)
    print("WAIT_TIMEOUT")
    return 2


if __name__ == "__main__":
    sys.exit(main())
