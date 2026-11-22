"""纯预报测试卡组启动入口"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import main

main.DEFAULT_DECK_POOL[:] = (
    ["kards:card_forecast"] * 36
    + ["kards:card_44th_silesia"] * 3
)
main.main()
