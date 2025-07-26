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
    CodeBlockNode,
    ImageNode,
    InlineMathNode,
    BlockMathNode,
    ForcedBreakNode,
    TableNode,
    PageBreakNode,
    TocNode,
)
from typing import List
import re


class Parser:
    # takes a list of tokens and transforms it into AST (document structure)
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0
        
        # Map token types to their parsing methods
        self.statement_parsers = {
            TokenType.HEADING: self._parse_heading,
            TokenType.BULLET_ITEM: self._parse_list,
            TokenType.NUMBERED_ITEM: self._parse_list,
            TokenType.PARAGRAPH: self._parse_paragraph,
            TokenType.HORIZONTAL_RULE: self._parse_horizontal_rule,
            TokenType.BLANK_LINE: self._parse_blank_line,
            TokenType.INDENTED_TEXT: self._parse_indented_text,
            TokenType.IMAGE: self._parse_image,
            TokenType.CODE_BLOCK: self._parse_code_block,
            TokenType.BLOCK_MATH: self._parse_block_math,
            TokenType.TABLE: self._parse_table,
            TokenType.PAGE_BREAK: self._parse_page_break,
            TokenType.TOC: self._parse_toc,
        }

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
    
    def _parse_toc(self) -> TocNode:
        """Parses a TOC token into a TocNode."""
        self._advance()
        return TocNode()
    
    def _parse_page_break(self) -> PageBreakNode:
        """Parses a PAGE_BREAK token into a PageBreakNode."""
        self._advance()
        return PageBreakNode()

    def _parse_statement(self) -> Node:
        """determines the type of the current token and calls the appropriate method to parse it"""
        token_type = self._peek().type
        
        parser_method = self.statement_parsers.get(token_type)
        
        if parser_method:
            return parser_method()

        # if token_type == TokenType.HEADING:
        #     return self._parse_heading()
        
        # if token_type in [TokenType.BULLET_ITEM, TokenType.NUMBERED_ITEM]:
        #     return self._parse_list()
        # if token_type == TokenType.PARAGRAPH:
        #     return self._parse_paragraph()
        # if token_type == TokenType.HORIZONTAL_RULE:
        #     return self._parse_horizontal_rule()
        # if token_type == TokenType.BLANK_LINE:
        #     self._advance()
        #     return BlankLineNode()
        # if token_type == TokenType.INDENTED_TEXT:
        #     return self._parse_indented_text()
        # if token_type == TokenType.IMAGE:
        #     return self._parse_image()
        # if token_type == TokenType.CODE_BLOCK:
        #     return self._parse_code_block()
        # if token_type == TokenType.BLOCK_MATH:
        #     return self._parse_block_math()
            

        self._advance()
        return None

    def _parse_blank_line(self) -> Node:
        # Check for multiple blank lines to create a forced break.
        if (self.current_token_index + 1) < len(self.tokens):
            next_token = self.tokens[self.current_token_index + 1]
            if next_token.type == TokenType.BLANK_LINE:
                # Consume both blank line tokens
                self._advance() 
                self._advance()
                # --- FIX #2: Call ForcedBreakNode with the required argument ---
                # Two blank lines create one line of extra space.
                return ForcedBreakNode(num_lines=1)

        # If it's just a single blank line, parse it normally.
        self._advance()
        return BlankLineNode()
    
    def _parse_inline_elements(self, text: str) -> List[Node]:
        """parses a string for inline elements like bold, italic, links, etc."""
        pattern = re.compile(r"""
            \*{2}(.*?)\*{2}         # Group 1: Bold (**...**)
            | \*(.*?)\*             # Group 2: Italic (*...*)
            | `(.*?)`               # Group 3: Inline Code (`...`)
            | !\[(.*?)\]\((.*?)\)   # Groups 4 & 5: Image (![...](...))
            | \[(.*?)\]\((.*?)\)    # Groups 6 & 7: Link ([...](...))
            | \$(.*?)\$             # Group 8: Inline Math ($...$)
        """, re.VERBOSE)
        nodes = []
        last_index = 0

        for match in pattern.finditer(text):
            if match.start() > last_index:
                nodes.append(TextNode(text[last_index : match.start()]))

            # Group 1: Bold
            if match.group(1) is not None:
                nodes.append(BoldNode(self._parse_inline_elements(match.group(1))))
            # Group 2: Italic
            elif match.group(2) is not None:
                nodes.append(ItalicNode(self._parse_inline_elements(match.group(2))))
            # Group 3: Inline Code
            elif match.group(3) is not None:
                nodes.append(CodeNode(match.group(3)))
            # Group 4 & 5: Image
            elif match.group(4) is not None:
                nodes.append(ImageNode(alt_text=match.group(4), url=match.group(5), caption=match.group(4)))
            # Group 6 & 7: Link
            elif match.group(6) is not None:
                link_text_nodes = self._parse_inline_elements(match.group(6))
                nodes.append(LinkNode(url=match.group(7), children=link_text_nodes))
            # Group 8: Inline Math
            elif match.group(8) is not None:
                nodes.append(InlineMathNode(match.group(8)))

            last_index = match.end()

        if last_index < len(text):
            nodes.append(TextNode(text[last_index:]))

        return nodes
    
    def _parse_block_math(self) -> BlockMathNode:
        """Parses a BLOCK_MATH token into a BlockMathNode."""
        token = self._peek()
        self._advance()
        return BlockMathNode(content=token.value)
    
    def _parse_image(self) -> ImageNode:
        """Parses an IMAGE token into an ImageNode."""
        token = self._peek()
        # The value is the dictionary we created in the tokenizer
        alt_text = token.value["alt"]
        url = token.value["url"]
        figure_type = "Image"  # default
        caption = alt_text  # default caption is the alt text
        
        if ":" in alt_text:
            parts = alt_text.split(":", 1)
            potential_type = parts[0].strip()
            if potential_type:
                figure_type = potential_type
                caption = parts[1].strip()
        
        
        self._advance()
        return ImageNode(alt_text=alt_text, url=url, caption=caption, figure_type=figure_type)

    def _parse_code_block(self) -> CodeBlockNode:
        """Parses a CODE_BLOCK token into a CodeBlockNode."""
        token = self._peek()
        language = token.value.get('language', 'text') or 'text'
        content = token.value.get("content", "")
        self._advance()
        return CodeBlockNode(content=content, language=language)


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

    def _parse_table(self) -> TableNode:
        token = self._peek()
        lines = [line for line in token.value.strip().split('\n') if line.strip()]
        
        metadata = {}
        data_lines = []
        
        for line in lines:
            if ":" in line and "|" not in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
            else:
                data_lines.append(line)
        
        headers = []
        rows = []
        
        if len(data_lines) >= 2:
            headers = [h.strip() for h in data_lines[0].strip('| \t').split('|')]
            for row_line in data_lines[2:]:
                row = [cell.strip() for cell in row_line.strip('| \t').split('|')]
                rows.append(row)
        
        self._advance()
        
        return TableNode(
            headers=headers, 
            rows=rows, 
            caption=metadata.get('caption', ''),
        )