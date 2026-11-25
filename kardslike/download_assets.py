"""
download_assets.py

从 kardsdecker CDN 下载 KARDS 卡面素材并解压到 mods/kards/assets

目录结构:
    mods/kards/assets/cards/{国家}/  普通卡图(按国家分, 已含中文卡面)
    mods/kards/assets/cards/altart/  异画(未绑定国家, 需手动归档)
    mods/kards/assets/cards/HQ/      HQ 卡图(跨国家战场图)
    mods/kards/assets/ui/            界面素材(待补充)
    mods/kards/data/zh.json          中文卡牌名称与描述

数据来源为 kardsdecker 的资源包, 遵循 1939 Games 社区内容政策, 仅限非商业使用

用法:
    python download_assets.py
"""
import json
import re
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR: Path = Path(__file__).resolve().parent
CACHE_DIR: Path = BASE_DIR / ".cache"
CARDS_DIR: Path = BASE_DIR / "mods" / "kards" / "assets" / "cards"
UI_DIR: Path = BASE_DIR / "mods" / "kards" / "assets" / "ui"
DATA_DIR: Path = BASE_DIR / "mods" / "kards" / "data"

# 全量卡图与数据包(约 670MB), 直链失效时请到下载站 https://1939.kardsdecker.com/gallery/download 获取最新地址
FULL_ZIP: str = "https://kards-assets.kardsdecker.com/KARDS_Database%20(2026-9-11,%20v53%20img,%20v53%20data).zip"

# 异画包(约 35MB)
ALTART_ZIP: str = "https://kards-assets.kardsdecker.com/altart%20(2026-9-21,%20v53%20img).zip"

# HQ 卡图名单与图片地址
HQ_NAMES_URL: str = "https://kards-assets.kardsdecker.com/HQ2_unknown-id_Resized/hq_names.json"
HQ_IMG_BASE: str = "https://kards-assets.kardsdecker.com/HQ2_unknown-id_Resized"

# 是否下载异画包
INCLUDE_ALTART: bool = True

# 下载分块大小(1MB)
CHUNK: int = 1 << 20

USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def head_length(url: str) -> int:
    """获取远程文件总大小

    Args:
        url: 文件地址

    Returns:
        文件字节数
    """
    req = Request(url, method="HEAD", headers={"user-agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        return int(resp.headers.get("Content-Length", "0"))


def download(url: str, dest: Path) -> None:
    """下载文件, 支持断点续传

    Args:
        url: 文件地址
        dest: 保存路径
    """
    total = head_length(url)
    if dest.exists() and dest.stat().st_size == total:
        print(f"已存在, 跳过 {dest.name}")
        return
    start = dest.stat().st_size if dest.exists() else 0
    if start > total:
        dest.unlink()
        start = 0
    headers = {"user-agent": USER_AGENT}
    if start > 0:
        headers["Range"] = f"bytes={start}-"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=120) as resp:
        if start > 0 and resp.status == 200:
            dest.unlink()
            start = 0
        mode = "ab" if start > 0 else "wb"
        received = start
        printed: set[int] = set()
        with open(dest, mode) as f:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                pct = received * 100 // total if total else 100
                if pct % 10 == 0 and pct not in printed:
                    print(f"  {dest.name} {pct}%")
                    printed.add(pct)
    print(f"下载完成 {dest.name} ({received} 字节)")


def extract_database(zip_path: Path) -> int:
    """从全量包提取普通卡图, 输出为 cards/{国家}/{card}.png

    Args:
        zip_path: 全量包路径

    Returns:
        新提取的图片数量
    """
    count = 0
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".png"):
                continue
            parts = Path(name).parts
            if len(parts) < 4:
                continue
            nation = parts[1]
            fname = parts[-1]
            dest = CARDS_DIR / nation / fname
            if dest.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, open(dest, "wb") as out:
                out.write(src.read())
            count += 1
    return count


def extract_altart(zip_path: Path) -> int:
    """从异画包提取卡图, 输出为 cards/altart/{card}.png

    Args:
        zip_path: 异画包路径

    Returns:
        新提取的图片数量
    """
    count = 0
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".png"):
                continue
            fname = Path(name).name
            dest = CARDS_DIR / "altart" / fname
            if dest.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, open(dest, "wb") as out:
                out.write(src.read())
            count += 1
    return count


def extract_zh(zip_path: Path) -> int:
    """从全量包提取中文卡牌名称与描述, 输出为 data/zh.json

    Args:
        zip_path: 全量包路径

    Returns:
        提取的卡牌数量
    """
    table: dict[str, dict[str, object]] = {}
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.endswith("/raw_data.json"):
                continue
            data = json.loads(zf.read(name).decode("utf-8-sig"))
            for item in data:
                info = item["node"]["json"]
                card_id = info.get("id")
                if not card_id:
                    continue
                image = info.get("image", "")
                table[card_id] = {
                    "id": card_id,
                    "title": info.get("title", {}).get("zh-Hans", ""),
                    "text": info.get("text", {}).get("zh-Hans", ""),
                    "title_en": info.get("title", {}).get("en-EN", ""),
                    "image": image.rsplit(".", 1)[0] if image else card_id,
                    "type": info.get("type", ""),
                    "faction": info.get("faction", ""),
                    "kredits": info.get("kredits", 0),
                    "attack": info.get("attack", 0),
                    "defense": info.get("defense", 0),
                    "operation_cost": info.get("operationCost", 0),
                    "rarity": info.get("rarity", ""),
                    "attributes": info.get("attributes", []),
                }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "zh.json").write_text(json.dumps(table, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(table)


def build_art_index() -> int:
    """根据中文数据与已下载的英文卡图生成索引

    Returns:
        索引条目数量
    """
    zh_path = DATA_DIR / "zh.json"
    if not zh_path.is_file():
        return 0
    table = json.loads(zh_path.read_text(encoding="utf-8-sig"))
    index: dict[str, dict[str, str]] = {}
    for card_id, record in table.items():
        faction = str(record.get("faction", ""))
        image = CARDS_DIR / faction / f"{card_id}.png"
        if not image.is_file():
            continue
        title = str(record.get("title", ""))
        rel = f"{faction}/{card_id}.png"
        index[f"card_{card_id}"] = {"title": title, "path": rel}
        if title:
            index[title] = {"title": title, "path": rel}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "art_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    name_map = {
        card_id: {
            "en": str(record.get("title_en", "")),
            "zh": str(record.get("title", "")),
            "faction": str(record.get("faction", "")),
            "type": str(record.get("type", "")),
        }
        for card_id, record in table.items()
    }
    (DATA_DIR / "name_map.json").write_text(
        json.dumps(name_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(index)


def fetch_hq_names() -> list[str]:
    """获取 HQ 卡图名单

    Returns:
        HQ 卡图文件名列表
    """
    req = Request(HQ_NAMES_URL, headers={"user-agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return list(data.keys())


def download_hq() -> int:
    """下载全部 HQ 卡图, 输出为 cards/HQ/{name}.png

    Returns:
        新下载的图片数量
    """
    names = fetch_hq_names()
    count = 0
    for name in names:
        dest = CARDS_DIR / "HQ" / f"{name}.png"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = Request(f"{HQ_IMG_BASE}/{name}.png", headers={"user-agent": USER_AGENT})
        try:
            with urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
                f.write(resp.read())
        except (HTTPError, URLError, OSError) as exc:
            print(f"HQ 下载失败 {name}: {exc}")
            continue
        count += 1
    return count


def main() -> None:
    """下载并解压卡面素材"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)

    full_zip = CACHE_DIR / "full.zip"
    print(f"下载全量包: {full_zip.name}")
    try:
        download(FULL_ZIP, full_zip)
        n = extract_database(full_zip)
        print(f"普通卡图新提取 {n} 张")
        n = extract_zh(full_zip)
        print(f"中文卡牌数据 {n} 条")
        n = build_art_index()
        print(f"卡图索引 {n} 条")
    except (HTTPError, URLError, OSError) as exc:
        print(f"全量包处理失败: {exc}")

    if INCLUDE_ALTART:
        altart_zip = CACHE_DIR / "altart.zip"
        print(f"下载异画包: {altart_zip.name}")
        try:
            download(ALTART_ZIP, altart_zip)
            n = extract_altart(altart_zip)
            print(f"异画卡图新提取 {n} 张")
        except (HTTPError, URLError, OSError) as exc:
            print(f"异画包处理失败: {exc}")

    print("下载 HQ 卡图")
    n = download_hq()
    print(f"HQ 卡图新下载 {n} 张")

    print("完成")


if __name__ == "__main__":
    main()
