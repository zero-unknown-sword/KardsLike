"""KardsLiker 的 KL 语言解析骨架。

支持两种写法：

1. 旧版 card 块：
    card "示例" { type: infantry, cost: 1 }

2. 声明式 SET_UNIT：
    IMPORT
        kards
    DEPENDENCIES
        kards
    SET_UNIT
        NAME: "近卫步兵第 8 团"
        CT/COST: 2
        OC/OPERATION_COST: 2
        AT: 3
        DF: 4
        TYPE: infantry
        COUNTRY: SovietUnion/SU
        RARE: ELITE
        DESCRIPTION: "..."
    SET_PROCEDURES
        { ... }
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Token:
    """KL token。"""

    kind: str
    value: str
    line: int
    column: int


class KLError(ValueError):
    """KL 语法错误。"""


KEYWORDS = {"card", "true", "false", "null"}
SECTION_NAMES = {
    "IMPORT",
    "IMPORTS",
    "DEPEND",
    "DEPENDS",
    "DEPENDENCY",
    "DEPENDENCIES",
    "REQUIRE",
    "REQUIRES",
    "SET_UNIT",
    "SET_PROCEDURES",
}
TYPE_ALIASES = {
    "inf": "infantry",
    "infantry": "infantry",
    "tank": "tank",
    "tk": "tank",
    "art": "artillery",
    "artillery": "artillery",
    "ftr": "fighter",
    "fighter": "fighter",
    "bmb": "bomber",
    "bomber": "bomber",
    "ord": "order",
    "order": "order",
    "ctr": "countermeasure",
    "countermeasure": "countermeasure",
    "步兵": "infantry",
    "坦克": "tank",
    "炮兵": "artillery",
    "火炮": "artillery",
    "战斗机": "fighter",
    "轰炸机": "bomber",
    "指令": "order",
    "反制": "countermeasure",
}
COUNTRY_ALIASES = {
    "sovietunion": "soviet",
    "su": "soviet",
    "ge": "germany",
    "de": "germany",
    "br": "britain",
    "uk": "britain",
    "jp": "japan",
    "us": "usa",
    "usa": "usa",
    "fr": "france",
    "it": "italy",
    "pl": "poland",
    "fi": "finland",
    "an": "anzac",
    "ne": "neutral",
    "ussr": "soviet",
    "soviet": "soviet",
    "britain": "britain",
    "uk": "britain",
    "germany": "germany",
    "ger": "germany",
    "japan": "japan",
    "jp": "japan",
    "usa": "usa",
    "us": "usa",
    "france": "france",
    "fr": "france",
    "italy": "italy",
    "it": "italy",
    "poland": "poland",
    "pl": "poland",
    "finland": "finland",
    "fi": "finland",
    "anzac": "anzac",
    "neutral": "neutral",
}
SECTION_ORDER = {
    "IMPORT": 0,
    "IMPORTS": 0,
    "DEPEND": 1,
    "DEPENDS": 1,
    "DEPENDENCY": 1,
    "DEPENDENCIES": 1,
    "REQUIRE": 1,
    "REQUIRES": 1,
    "SET_UNIT": 2,
    "SET_PROCEDURES": 3,
}
RARITY_ALIASES = {
    "普通": "standard",
    "标准": "standard",
    "standard": "standard",
    "限定": "limited",
    "limited": "limited",
    "特殊": "special",
    "special": "special",
    "精英": "elite",
    "elite": "elite",
    "emlite": "elite",
    "衍生": "none",
    "none": "none",
}


def tokenize(source: str) -> list[Token]:
    """把旧版 KL 源码切成 token。"""
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1
    length = len(source)

    def advance(text: str) -> None:
        nonlocal line, column
        for char in text:
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1

    while i < length:
        char = source[i]
        if char in " \t\r\n":
            advance(char)
            i += 1
            continue
        if char == "#":
            end = source.find("\n", i)
            if end < 0:
                end = length
            advance(source[i:end])
            i = end
            continue
        if char in "{}:,":
            tokens.append(Token(char, char, line, column))
            advance(char)
            i += 1
            continue
        if char == '"':
            start_line, start_column = line, column
            j = i + 1
            value: list[str] = []
            while j < length and source[j] != '"':
                if source[j] == "\\" and j + 1 < length:
                    value.append(source[j + 1])
                    j += 2
                else:
                    value.append(source[j])
                    j += 1
            if j >= length:
                raise KLError(f"第 {start_line} 行字符串未闭合")
            text = source[i : j + 1]
            tokens.append(Token("STRING", "".join(value), start_line, start_column))
            advance(text)
            i = j + 1
            continue
        if char.isdigit() or (char == "-" and i + 1 < length and source[i + 1].isdigit()):
            j = i + 1
            while j < length and source[j].isdigit():
                j += 1
            text = source[i:j]
            tokens.append(Token("NUMBER", text, line, column))
            advance(text)
            i = j
            continue
        if char.isalpha() or char == "_":
            j = i + 1
            while j < length and (source[j].isalnum() or source[j] == "_"):
                j += 1
            text = source[i:j]
            kind = "KEYWORD" if text in KEYWORDS else "IDENT"
            tokens.append(Token(kind, text, line, column))
            advance(text)
            i = j
            continue
        raise KLError(f"第 {line} 行第 {column} 列存在未知字符: {char!r}")
    tokens.append(Token("EOF", "", line, column))
    return tokens


class Parser:
    """旧版 card 块解析器。"""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def current(self) -> Token:
        return self.tokens[self.index]

    def consume(self, kind: str | None = None, value: str | None = None) -> Token:
        token = self.current()
        if kind is not None and token.kind != kind:
            raise KLError(f"第 {token.line} 行需要 {kind}, 实际为 {token.kind}")
        if value is not None and token.value != value:
            raise KLError(f"第 {token.line} 行需要 {value!r}, 实际为 {token.value!r}")
        self.index += 1
        return token

    def parse(self) -> list[dict[str, Any]]:
        cards: list[dict[str, Any]] = []
        while self.current().kind != "EOF":
            if self.current().kind == "KEYWORD" and self.current().value == "card":
                cards.append(self.parse_card())
            else:
                token = self.current()
                raise KLError(f"第 {token.line} 行只允许 card 声明")
        return cards

    def parse_card(self) -> dict[str, Any]:
        self.consume("KEYWORD", "card")
        name = self.consume("STRING").value
        self.consume("{")
        fields: dict[str, Any] = {}
        while self.current().kind != "}":
            key = self.consume("IDENT").value
            self.consume(":")
            fields[key] = self.parse_value()
            if self.current().kind == ",":
                self.consume(",")
        self.consume("}")
        return {"name": name, "fields": fields}

    def parse_value(self) -> Any:
        token = self.current()
        if token.kind == "STRING":
            self.consume("STRING")
            return token.value
        if token.kind == "IDENT":
            self.consume("IDENT")
            return token.value
        if token.kind == "NUMBER":
            self.consume("NUMBER")
            return int(token.value)
        if token.kind == "KEYWORD":
            self.consume("KEYWORD")
            if token.value == "true":
                return True
            if token.value == "false":
                return False
            return None
        raise KLError(f"第 {token.line} 行字段值不合法: {token.value!r}")


def _strip_commas(value: str) -> str:
    return value.strip().rstrip(",").strip()


def _parse_scalar(value: str) -> Any:
    value = _strip_commas(value)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"')
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",")]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _normalize_type(value: str) -> str:
    cleaned = value.strip().strip("（）()").strip().lower()
    return TYPE_ALIASES.get(cleaned, cleaned)


def _normalize_country(value: str) -> str:
    cleaned = value.strip().strip('"').lower()
    cleaned = cleaned.rsplit("/", 1)[-1].strip()
    return COUNTRY_ALIASES.get(cleaned, cleaned)


def _normalize_rarity(value: str) -> str:
    cleaned = value.strip().strip('"').lower()
    return RARITY_ALIASES.get(cleaned, cleaned)


def _section_name(line: str) -> str | None:
    stripped = line.strip().rstrip(":").upper()
    return stripped if stripped in SECTION_NAMES else None


def _collect_section(lines: list[str], start: int) -> tuple[list[str], int]:
    collected: list[str] = []
    index = start
    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        if _section_name(raw) is not None:
            break
        collected.append(raw.strip())
        index += 1
    return collected, index


ALLOWED_TYPES = {"infantry", "tank", "artillery", "fighter", "bomber", "order", "countermeasure"}
ALLOWED_COUNTRIES = {
    "germany", "britain", "japan", "soviet", "usa", "france",
    "italy", "poland", "finland", "anzac", "neutral",
}
ALLOWED_RARITIES = {"standard", "limited", "special", "elite", "none"}
INTEGER_FIELDS = {
    "cost": (0, 99),
    "operation_cost": (0, 9),
    "at": (0, 99),
    "df": (0, 99),
}
KNOWN_FIELDS = {
    "name", "id", "cost", "operation_cost", "at", "df",
    "type", "country", "rarity", "keywords", "text", "art",
}


def validate_card(card: dict[str, Any]) -> list[str]:
    """检查 SET_UNIT 字段类型并返回警告。"""
    fields = card.get("fields")
    if not isinstance(fields, dict):
        raise KLError("SET_UNIT 缺少字段")
    errors: list[str] = []
    warnings: list[str] = []
    name = str(fields.get("name", "")).strip()
    if not name:
        errors.append("NAME 不能为空")
    id_value = fields.get("id")
    if id_value is None:
        warnings.append("ID 未填写，保存时会自动生成")
    elif not isinstance(id_value, str):
        errors.append("ID 必须是字符串")
    elif not re.fullmatch(r"[a-z][a-z0-9_]*", id_value):
        warnings.append("ID 建议使用小写字母、数字和下划线")
    for key, (minimum, maximum) in INTEGER_FIELDS.items():
        value = fields.get(key)
        if value is None:
            warnings.append(f"{key} 未填写，按 0 处理")
            continue
        if not isinstance(value, int):
            errors.append(f"{key} 必须是整数")
        elif not minimum <= value <= maximum:
            errors.append(f"{key} 必须在 {minimum}..{maximum} 之间")
    if "type" in fields and fields["type"] not in ALLOWED_TYPES:
        errors.append(f"TYPE 无效: {fields['type']!r}")
    if "country" in fields and fields["country"] not in ALLOWED_COUNTRIES:
        errors.append(f"COUNTRY 无效: {fields['country']!r}")
    if "rarity" in fields and fields["rarity"] not in ALLOWED_RARITIES:
        errors.append(f"RARE 无效: {fields['rarity']!r}")
    if fields.get("keywords") is not None and not isinstance(fields["keywords"], list):
        errors.append("KEYWORDS 必须是列表")
    if not str(fields.get("text", "")).strip():
        warnings.append("DESCRIPTION 为空")
    unknown = sorted(set(fields) - KNOWN_FIELDS)
    if unknown:
        warnings.append("未知字段: " + ", ".join(unknown))
    if errors:
        raise KLError("类型检查失败：" + "；".join(errors))
    return warnings


def parse_declarations(source: str) -> list[dict[str, Any]]:
    """解析 SET_UNIT 声明式语法。"""
    lines = source.splitlines()
    imports: list[str] = []
    dependencies: list[str] = []
    fields: dict[str, Any] = {}
    procedures = ""
    warnings: list[str] = []
    quote_errors: list[str] = []
    field_indent: int | None = None
    index = 0
    last_order = -1
    while index < len(lines):
        section = _section_name(lines[index])
        if section is None:
            stripped = lines[index].strip()
            if stripped and not lines[index].startswith((" ", "\t")) and re.fullmatch(r"[A-Z][A-Z0-9_]*", stripped):
                warnings.append(f"未知数据段: {stripped}")
            index += 1
            continue
        order = SECTION_ORDER.get(section, -1)
        if order < last_order:
            raise KLError(
                "段顺序错误：必须按 IMPORT -> DEPENDENCIES -> "
                "SET_UNIT -> SET_PROCEDURES 排列"
            )
        last_order = order
        if section in {"IMPORT", "IMPORTS"}:
            values, index = _collect_section(lines, index + 1)
            for value in values:
                cleaned = _strip_commas(value)
                if cleaned.lower().startswith("keywords:"):
                    fields["keywords"] = _parse_scalar(cleaned.split(":", 1)[1])
                elif cleaned:
                    imports.append(cleaned)
            continue
        if section in {"DEPEND", "DEPENDS", "DEPENDENCY", "DEPENDENCIES", "REQUIRE", "REQUIRES"}:
            values, index = _collect_section(lines, index + 1)
            dependencies.extend(_strip_commas(value) for value in values if _strip_commas(value))
            continue
        if section == "SET_UNIT":
            index += 1
            while index < len(lines):
                raw = lines[index]
                stripped = raw.strip()
                if not stripped:
                    index += 1
                    continue
                if _section_name(raw) is not None:
                    break
                if ":" not in stripped:
                    index += 1
                    continue
                indent = len(raw) - len(raw.lstrip(" "))
                if field_indent is None:
                    field_indent = indent
                elif indent != field_indent:
                    warnings.append(
                        f"SET_UNIT 缩进不一致：第 {index + 1} 行应为 {field_indent} 个空格"
                    )
                key, value = stripped.split(":", 1)
                key = key.strip().upper().replace(" ", "_")
                key_options = {key, *key.split("/")}
                value = value.strip()
                if key_options & {"NAME", "ID", "DESCRIPTION", "TEXT", "BODY"}:
                    if not (value.startswith('"') or value.startswith('"""')):
                        quote_errors.append(f"{key} 必须使用双引号")
                if value.startswith('"""'):
                    collected: list[str] = [value[3:]]
                    index += 1
                    while index < len(lines) and '"""' not in lines[index]:
                        collected.append(lines[index])
                        index += 1
                    if index < len(lines):
                        collected.append(lines[index].split('"""', 1)[0])
                        index += 1
                    value = "\n".join(collected).strip("\n")
                    fields["text"] = value
                    continue
                if "NAME" in key_options:
                    fields["name"] = _parse_scalar(value)
                elif key_options & {"CT", "COST"}:
                    fields["cost"] = _parse_scalar(value)
                elif key_options & {"OC", "OPERATION_COST", "OPERATIONCOST", "OP"}:
                    fields["operation_cost"] = _parse_scalar(value)
                elif key_options & {"AT", "ATTACK"}:
                    fields["at"] = _parse_scalar(value)
                elif key_options & {"DF", "DEFENSE", "DEFENCE"}:
                    fields["df"] = _parse_scalar(value)
                elif "TYPE" in key_options:
                    fields["type"] = _normalize_type(str(_parse_scalar(value)))
                elif key_options & {"COUNTRY", "FACTION"}:
                    fields["country"] = _normalize_country(str(_parse_scalar(value)))
                elif key_options & {"RARE", "RARITY"}:
                    fields["rarity"] = _normalize_rarity(str(_parse_scalar(value)))
                elif "KEYWORDS" in key_options:
                    fields["keywords"] = _parse_scalar(value)
                elif key_options & {"DESCRIPTION", "TEXT", "BODY"}:
                    fields["text"] = _parse_scalar(value)
                elif "ID" in key_options:
                    fields["id"] = _parse_scalar(value)
                index += 1
            continue
        if section == "SET_PROCEDURES":
            index += 1
            collected = []
            depth = 0
            while index < len(lines):
                raw = lines[index]
                for char in raw:
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                collected.append(raw)
                index += 1
                if depth <= 0 and "}" in "".join(collected):
                    break
            procedures = "\n".join(collected).strip()
            continue
        index += 1
    if quote_errors:
        raise KLError("字符串字段必须使用双引号：" + "；".join(quote_errors))
    name = str(fields.get("name", fields.get("id", "未命名卡牌")))
    card = {
        "name": name,
        "fields": fields,
        "procedures": procedures,
        "imports": imports,
        "dependencies": dependencies,
    }
    card["warnings"] = warnings + validate_card(card)
    return [card]


def parse(source: str) -> list[dict[str, Any]]:
    """解析 KL 源码并返回卡牌 AST。"""
    if re.search(r"(?im)^\s*(?:SET_UNIT|IMPORT|DEPENDENCIES|SET_PROCEDURES)\b", source):
        return parse_declarations(source)
    return Parser(tokenize(source)).parse()
