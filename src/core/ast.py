# define the classes for AST nodes (structure of the document)

# 1. define a template that all other AST nodes will be based on
from typing import List
from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def accept(self, visitor):  # must be implemented by all child nodes
        pass


class DocumentNode(Node):
    """root node of the tree, represents the entire document"""

    def __init__(self):
        self.children: List[Node] = []  # empty list called children

    def accept(self, visitor):
        return visitor.visit_document(self)


class ParagraphNode(Node):
    """represents a paragraph in the document"""

    def __init__(self):
        self.children: List[Node] = []  # text of the paragraph

    def accept(self, visitor):
        return visitor.visit_paragraph(self)


class HeadingNode(Node):
    """represents a heading"""

    def __init__(self, level: int, text: str):
        self.level = level
        self.text = text

    def accept(self, visitor):
        return visitor.visit_heading(self)


class HorizontalRuleNode(Node):
    """represents a horizontal rule (---)"""

    def accept(self, visitor):
        return visitor.visit_horizontal_rule(self)


class ListNode(Node):
    """represents an entire list (bullet or numered)"""

    def __init__(self, list_type: str):
        self.list_type = list_type
        self.items: List["ListItemNode"] = []

    def accept(self, visitor):
        return visitor.visit_list(self)


class ListItemNode(Node):
    """represents a single item wihtin a list"""

    def __init__(self):
        self.children: List[Node] = []

    def accept(self, visitor):
        return visitor.visit_list_item(self)


class BlankLineNode(Node):
    """represents a blank line"""

    def accept(self, visitor):
        return visitor.visit_blank_line(self)


class IndentedTextNode(Node):
    """>> syntax for indented text"""

    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor):
        return visitor.visit_indented_text(self)


class TextNode(Node):
    """represents a plain text segment"""

    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor):
        return visitor.visit_text(self)


class BoldNode(Node):
    """represents bold text"""

    def __init__(self, children: List[Node]):
        self.children = children

    def accept(self, visitor):
        return visitor.visit_bold(self)


class ItalicNode(Node):
    """Represents italic text (*...*)."""

    def __init__(self, children: List[Node]):
        self.children = children

    def accept(self, visitor):
        return visitor.visit_italic(self)


class CodeNode(Node):
    """Represents inline code (`...`)."""

    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor):
        return visitor.visit_code(self)


class LinkNode(Node):
    """Represents a hyperlink ([text](url))."""

    def __init__(self, url: str, children: List[Node]):
        self.url = url
        self.children = children

    def accept(self, visitor):
        return visitor.visit_link(self)
