from .tokenizer import Token, TokenType
from .ast import *
from typing import List, Dict

class Parser:
    # takes a list of tokens and transforms it into AST (document structure)
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0
    
    def _peek(self) -> Token:
        """looks at the current token without consuming it"""
        return self.tokens[self.current_token_index]
    
    def _advance(self) -> None:
        """consumes the current token and moves to the next one"""
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
    
    def parse(self) -> DocumentNode:
        """main method loops through tokens and builds the complete AST"""
        document = DocumentNode()
        # loop until we reach the EOF token
        while self._peek().type != TokenType.EOF:
            node = self._parse_statement()
            if node:
                document.children.append(node)
        return document

    def _parse_statement(self) -> Node:
        """determines the type of the current token and calls the appropriate method to parse it"""
        token_type = self._peek().type
        
        if token_type == TokenType.HEADING:
            return self._parse_heading()
        if token_type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]:
            return self._parse_list()
        if token_type == TokenType.PARAGRAPH:
            return self._parse_paragraph()
        if token_type == TokenType.HORIZONTAL_RULE:
            return self._parse_horizontal_rule()
        if token_type == TokenType.BLANK_LINE:
            self._advance()
            return BlankLineNode()
        if token_type == TokenType.INDENTED_TEXT:
            return self._parse_indented_text()
        # TODO: list parsing
        
        self._advance()
        return None
    
    def _parse_heading(self) -> HeadingNode:
        """parses a HEADING token into a HeadingNode"""
        token = self._peek()
        self._advance()
        return HeadingNode(level=token.level, text=token.value)
    
    def _parse_paragraph(self) -> ParagraphNode:
        """parses a PARAGRAPH token into a ParagraphNode"""
        token = self._peek()
        self._advance()
        return ParagraphNode(text=token.value)

    def _parse_horizontal_rule(self) -> HorizontalRuleNode:
        """parses a HORIZONTAL_RULE token into a HorizontalRuleNode"""
        self._advance()
        return HorizontalRuleNode()
    
    def _parse_indented_text(self) -> IndentedTextNode:
        """parses an INDENTED_TEXT token into an IndentedTextNode"""
        token = self._peek()
        self._advance()
        return IndentedTextNode(text=token.value)

    def _parse_list(self) -> ListNode:
        """parses a sequence of list item tokens into a ListNode (cann call itself recursively)"""
        # 1. Determine the list type and base indentation level
        base_indent = self._peek().indent
        list_type = "itemize" if self._peek().type == TokenType.BULLET_ITEM else "enumerate"
        list_node = ListNode(list_type=list_type)
        
        # 2. Loop as long as we are seeing list items with the same indentation
        while self._peek().type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM] and self._peek().indent >= base_indent:
            # 3. If the item is at our current level process it
            if self._peek().indent == base_indent:
                item_node = ListItemNode()
                item_node.children.append(ParagraphNode(text=self._peek().value))
                self._advance()
            
                # 4. if the next token is a list item with more indentation, it's a nested list
                if self._peek().type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM] and self._peek().indent > base_indent:
                    nested_list = self._parse_list()
                    item_node.children.append(nested_list)
            
                list_node.items.append(item_node)
            else:
                break
        return list_node

def extract_metadata(markdown_content: str) -> tuple[dict, str]:
    metadata: Dict[str, str] = {}
    lines = markdown_content.split("\n")
    return metadata, markdown_content