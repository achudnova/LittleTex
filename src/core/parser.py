from .tokenizer import Token, TokenType
from .ast import (
    Node,
    DocumentNode,
    ParagraphNode,
    HeadingNode,
    HorizontalRuleNode,
    ListNode,
    ListItemNode,
    BlankLineNode,
    IndentedTextNode,
    TextNode,
    BoldNode,
    ItalicNode,
    CodeNode,
    LinkNode,
    ImageNode,
)
from typing import List
import re


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
        if token_type == TokenType.IMAGE:
            return self._parse_image()
            

        self._advance()
        return None

    def _parse_inline_elements(self, text: str) -> List[Node]:
        """parses a string for inline elements like bold, italic, links, etc."""
        pattern = re.compile(r"\*{2}(.*?)\*{2}|\*(.*?)\*|`(.*?)`|\[(.*?)\]\((.*?)\)")
        nodes = []
        last_index = 0

        for match in pattern.finditer(text):
            if match.start() > last_index:
                nodes.append(TextNode(text[last_index : match.start()]))

            if match.group(1) is not None:  # Bold
                nodes.append(BoldNode(self._parse_inline_elements(match.group(1))))
            elif match.group(2) is not None:  # Italic
                nodes.append(ItalicNode(self._parse_inline_elements(match.group(2))))
            elif match.group(3) is not None:  # Inline code
                nodes.append(CodeNode(match.group(3)))
            elif match.group(4) is not None:  # Link
                link_text_nodes = self._parse_inline_elements(match.group(4))
                nodes.append(LinkNode(url=match.group(5), children=link_text_nodes))

            last_index = match.end()

        if last_index < len(text):
            nodes.append(TextNode(text[last_index:]))

        return nodes
    
    def _parse_image(self) -> ImageNode:
        """Parses an IMAGE token into an ImageNode."""
        token = self._peek()
        # The value is the dictionary we created in the tokenizer
        alt_text = token.value["alt"]
        url = token.value["url"]
        self._advance()
        return ImageNode(alt_text=alt_text, url=url)

    def _parse_heading(self) -> HeadingNode:
        """parses a HEADING token into a HeadingNode"""
        token = self._peek()
        self._advance()
        return HeadingNode(level=token.level, text=token.value)

    def _parse_paragraph(self) -> ParagraphNode:
        """parses a PARAGRAPH token into a ParagraphNode"""

        para_node = ParagraphNode()
        token = self._peek()
        para_node.children = self._parse_inline_elements(token.value.strip())
        self._advance()

        while self._peek().type == TokenType.PARAGRAPH:
            para_node.children.append(TextNode("\n"))

            token = self._peek()
            para_node.children.extend(self._parse_inline_elements(token.value.strip()))
            self._advance()

        return para_node

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
        list_type = (
            "itemize" if self._peek().type == TokenType.BULLET_ITEM else "enumerate"
        )
        list_node = ListNode(list_type=list_type)

        # 2. Loop as long as we are seeing list items with the same indentation
        while (
            self._peek().type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]
            and self._peek().indent >= base_indent
        ):
            # 3. If the item is at our current level process it
            if self._peek().indent == base_indent:
                item_node = ListItemNode()
                item_node.children.extend(
                    self._parse_inline_elements(self._peek().value)
                )
                self._advance()

                # 4. if the next token is a list item with more indentation, it's a nested list
                if (
                    self._peek().type
                    in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]
                    and self._peek().indent > base_indent
                ):
                    nested_list = self._parse_list()
                    item_node.children.append(nested_list)

                list_node.items.append(item_node)
            else:
                break
        return list_node
