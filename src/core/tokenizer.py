# Tokenizer - scan the input markdown string and produce a list of tokens

from typing import List
from enum import Enum, auto
import re


class TokenType(Enum):
    # enum for different types of tokens (set of named constants)
    # token.type == TokenType.HEADING
    # auto() - assings a unique integer value to each number
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
    EOF = auto()  # End of file token (signifies end of input)


class Token:
    # data class to hold all the information about a single token
    def __init__(
        self, token_type: TokenType, value: str = "", level: int = 0, indent: int = 0
    ):
        self.type = token_type
        self.value = value  # text content
        self.level = level  # heading level (1, 2, 3)
        self.indent = indent  # indentation level

    def __repr__(self) -> str:
        parts = [f"type={self.type.name}"]
        if self.value:
            parts.append(f"value='{self.value}'")
        if self.level:
            parts.append(f"level={self.level}")
        if self.indent:
            parts.append(f"indent={self.indent}")
        return f"Token({', '.join(parts)})"


# convert text into the Token objects
class Tokenizer:
    # list of tuples, where each tuple contains:
    # token type and a compiled regular expression to match the token
    TOKEN_RULES = [
        (TokenType.HEADING, re.compile(r"^(#{1,3})\s*(.*)")),
        (TokenType.BULLET_ITEM, re.compile(r"^\-\s+(.*)")),
        (TokenType.NUMBERED_ITEM, re.compile(r"^\d+\.\s+(.*)")),
        (TokenType.HORIZONTAL_RULE, re.compile(r"^---$")),
        (TokenType.INDENTED_TEXT, re.compile(r"^>>\s(.*)")),
        (TokenType.IMAGE, re.compile(r"^!\[(.*?)\]\((.*?)\)$")),
    ]

    # scan the raw md text & convert it into a list of Token objects
    def tokenize(self, markdown_content: str) -> List[Token]:
        # takes the whole md file as a string and returns a list of tokens
        tokens: List[Token] = []
        lines = markdown_content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip().startswith("```"):
                language = line.strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                
                content = "\n".join(code_lines)
                tokens.append(Token(TokenType.CODE_BLOCK, value={'language': language, 'content': content}))
                i += 1
            else:
                tokens.append(self._tokenize_line(line))
                i += 1
        
        tokens.append(Token(TokenType.EOF))  # Add EOF token at the end
        return tokens

    def _tokenize_line(self, line: str) -> Token:
        # analyzes a single line and return the appropriate Token for it
        stripped_line = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if not stripped_line:
            return Token(TokenType.BLANK_LINE)

        for token_type, regex in self.TOKEN_RULES:
            match = regex.match(stripped_line)
            if match:
                return self._create_token(token_type, match, indent)
        return Token(TokenType.PARAGRAPH, value=line)

    def _create_token(
        self, token_type: TokenType, match: re.Match, indent: int
    ) -> Token:
        """Method to create a token from a regex match"""
        if token_type == TokenType.HEADING:
            level = len(match.group(1))
            text = match.group(2)
            return Token(token_type, value=text, level=level)

        if token_type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]:
            text = match.group(1)
            return Token(token_type, value=text, indent=indent)

        if token_type == TokenType.INDENTED_TEXT:
            return Token(token_type, value=match.group(1))

        if token_type == TokenType.HORIZONTAL_RULE:
            return Token(token_type)

        if token_type == TokenType.IMAGE:
            alt_text = match.group(1)
            url = match.group(2)
            return Token(token_type, value={"alt": alt_text, "url": url})
        
