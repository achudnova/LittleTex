import re
from typing import List, Tuple, Optional
from enum import Enum, auto


class TokenType(Enum):
    HEADING = auto()
    BULLET_ITEM = auto()
    NUMBERED_ITEM = auto()
    HORIZONTAL_RULE = auto()
    INDENTED_TEXT = auto()
    PARAGRAPH = auto()
    BLANK_LINE = auto()
    LINK = auto()
    IMAGE = auto()
    CODE_BLOCK = auto()
    BLOCK_MATH = auto()
    TABLE = auto()
    PAGE_BREAK = auto()
    TOC = auto()
    EOF = auto()


class Token:
    def __init__(
        self, token_type: TokenType, value: any = "", level: int = 0, indent: int = 0
    ):
        self.type, self.value, self.level, self.indent = (
            token_type,
            value,
            level,
            indent,
        )

    def __repr__(self) -> str:
        parts = [f"type={self.type.name}"]
        if self.value:
            parts.append(f"value='{self.value}'")
        if self.level:
            parts.append(f"level={self.level}")
        if self.indent:
            parts.append(f"indent={self.indent}")
        return f"Token({', '.join(parts)})"


class Tokenizer:

    MULTI_LINE_BLOCK_RULES = {
        "```": (TokenType.CODE_BLOCK, "```"),
        "$$": (TokenType.BLOCK_MATH, "$$"),
        "::: table": (TokenType.TABLE, ":::"),
    }

    SINGLE_LINE_TOKEN_RULES = [
        (TokenType.TOC, re.compile(r"^@toc$")),
        (TokenType.PAGE_BREAK, re.compile(r"^@newpage.*$")),
        (TokenType.HEADING, re.compile(r"^(#{1,3})\s*(.*)")),
        (TokenType.IMAGE, re.compile(r"^!\[(.*?)\]\((.*?)\)$")),
        (TokenType.BULLET_ITEM, re.compile(r"^\-\s+(.*)")),
        (TokenType.NUMBERED_ITEM, re.compile(r"^\d+\.\s+(.*)")),
        (TokenType.HORIZONTAL_RULE, re.compile(r"^---$")),
        (TokenType.INDENTED_TEXT, re.compile(r"^>>\s(.*)")),
    ]

    def tokenize(self, markdown_content: str) -> List[Token]:
        """Tokenizes the entire document using a state machine approach."""
        tokens: List[Token] = []
        lines = markdown_content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # 1. Check if this line starts a multi-line block
            block_token, lines_consumed = self._try_parse_multi_line_block(lines, i)
            if block_token:
                tokens.append(block_token)
                i += lines_consumed
            else:
                # 2. If not, process it as a single line
                tokens.append(self._tokenize_line(line))
                i += 1

        tokens.append(Token(TokenType.EOF))
        return tokens

    def _try_parse_multi_line_block(
        self, lines: List[str], current_index: int
    ) -> Tuple[Optional[Token], int]:
        """
        Checks if the current line starts a multi-line block.
        If so, consumes the block and returns the token and number of lines consumed.
        If not, returns (None, 0).
        """
        line_content = lines[current_index].strip()

        for start_sequence, (
            token_type,
            end_sequence,
        ) in self.MULTI_LINE_BLOCK_RULES.items():
            # Check if the line starts with the block's opening sequence
            # For code blocks, we also need to handle the language specifier.
            if line_content.startswith(start_sequence):
                block_lines = []
                # For code blocks, extract the language
                language = (
                    line_content[len(start_sequence) :].strip()
                    if token_type == TokenType.CODE_BLOCK
                    else ""
                )

                # Start consuming lines from the next line
                i = current_index + 1
                while i < len(lines) and not lines[i].strip() == end_sequence:
                    block_lines.append(lines[i])
                    i += 1

                content = "\n".join(block_lines)

                # Create the correct token with the right value format
                if token_type == TokenType.CODE_BLOCK:
                    value = {"language": language, "content": content}
                else:
                    value = content

                token = Token(token_type, value=value)
                lines_consumed = (i - current_index) + 1
                return token, lines_consumed

        return None, 0

    def _tokenize_line(self, line: str) -> Token:
        stripped_line = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not stripped_line:
            return Token(TokenType.BLANK_LINE)
        for token_type, regex in self.SINGLE_LINE_TOKEN_RULES:
            match = regex.match(stripped_line)
            if match:
                return self._create_token_from_match(token_type, match, indent)
        return Token(TokenType.PARAGRAPH, value=line)

    def _create_token_from_match(
        self, token_type: TokenType, match: re.Match, indent: int
    ) -> Token:
        if token_type == TokenType.HEADING:
            level, text = len(match.group(1)), match.group(2)
            return Token(token_type, value=text, level=level)
        if token_type == TokenType.IMAGE:
            alt_text, url = match.group(1), match.group(2)
            return Token(token_type, value={"alt": alt_text, "url": url})
        if token_type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]:
            return Token(token_type, value=match.group(1), indent=indent)
        if token_type == TokenType.INDENTED_TEXT:
            return Token(token_type, value=match.group(1))
        if token_type in [
            TokenType.HORIZONTAL_RULE,
            TokenType.PAGE_BREAK,
            TokenType.TOC,
        ]:
            return Token(token_type)
        raise ValueError(f"Unknown token type for match creation: {token_type}")
