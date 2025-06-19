# Tokenizer - scan the input markdown string and produce a list of tokens

from typing import List, Optional
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
    PARAGRAPH = auto()
    BLANK_LINE = auto()
    LINK = auto()
    EOF = auto()  # End of file token (signifies end of input)
    
class Token:
    # data class to hold all the information about a single token
    def __init__(self, token_type: TokenType, value: str = "", level: int = 0, indent: int = 0):
        self.type = token_type
        self.value = value      # text content
        self.level = level      # heading level (1, 2, 3)
        self.indent = indent    # indentation level
        
# convert text into the Token objects
class Tokenizer:
    # scan the raw md text & convert it into a list of Token objects
    def tokenize(self, markdown_content: str) -> List[Token]:
        # takes the whole md file as a string and returns a list of tokens
        tokens: List[Token] = []
        #lines = markdown_content.splitlines()
        for line in markdown_content.splitlines():
            tokens.append(self._tokenize_line(line))

        tokens.append(Token(TokenType.EOF))  # Add EOF token at the end
        return tokens
    
    def _tokenize_line(self, line: str) -> Token:
        # analyzes a single line and return the appropriate Token for it
        stripped_line = line.strip()
        indent = len(line) - len(line.lstrip(' '))
        
        if not stripped_line:
            return Token(TokenType.BLANK_LINE)
        
        if stripped_line == "---":
            return Token(TokenType.HORIZONTAL_RULE)
        
        heading_match = re.match(r'^(#{1,3})\s*(.*)', stripped_line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            return Token(TokenType.HEADING, value=text, level=level)
        
        bullet_match = re.match(r'^\-\s+(.*)', stripped_line)
        if bullet_match:
            text = bullet_match.group(1)
            return Token(TokenType.BULLET_ITEM, value=text, indent=indent)
    
        numered_match = re.match(r'^\d+\.\s+(.*)', stripped_line)
        if numered_match:
            text = numered_match.group(1)
            return Token(TokenType.NUMBERED_ITEM, value=text, indent=indent)
        
        return Token(TokenType.PARAGRAPH, value=line)