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


def parse_declarations(source: str) -> list[dict[str, Any]]:
    """解析 SET_UNIT 声明式语法。"""
    lines = source.splitlines()
    imports: list[str] = []
    dependencies: list[str] = []
    fields: dict[str, Any] = {}
    procedures = ""
    index = 0
    while index < len(lines):
        section = _section_name(lines[index])
        if section is None:
            index += 1
            continue
        if section in {"IMPORT", "IMPORTS"}:
            values, index = _collect_section(lines, index + 1)
            imports.extend(_strip_commas(value) for value in values if _strip_commas(value))
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
                key, value = stripped.split(":", 1)
                key = key.strip().upper().replace(" ", "_")
                key_options = {key, *key.split("/")}
                value = value.strip()
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
    name = str(fields.get("name", fields.get("id", "未命名卡牌")))
    return [
        {
            "name": name,
            "fields": fields,
            "procedures": procedures,
            "imports": imports,
            "dependencies": dependencies,
        }
    ]


def parse(source: str) -> list[dict[str, Any]]:
    """解析 KL 源码并返回卡牌 AST。"""
    if re.search(r"(?im)^\s*(?:SET_UNIT|IMPORT|DEPENDENCIES|SET_PROCEDURES)\b", source):
        return parse_declarations(source)
    return Parser(tokenize(source)).parse()
