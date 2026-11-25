"""KardsLiker 的 KL 语言解析骨架。

KL 是面向 KARDS mod 的声明式卡牌语言，目前支持：

    card "card_example" {
        type: infantry
        cost: 1
        at: 2
        df: 3
        text: "部署：抽 1 张牌。"
    }

现阶段只做词法分析和 AST 解析，不直接生成 Python。
"""
from __future__ import annotations

from dataclasses import dataclass, field
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


def tokenize(source: str) -> list[Token]:
    """把 KL 源码切成 token。"""
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
    """KL 递归下降解析器。"""

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


def parse(source: str) -> list[dict[str, Any]]:
    """解析 KL 源码并返回卡牌 AST。"""
    return Parser(tokenize(source)).parse()
