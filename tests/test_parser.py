import pytest
from src.core.tokenizer import Token, TokenType
from src.core.parser import Parser
from src.core.ast import DocumentNode, HeadingNode, ListNode, ListItemNode, TextNode

def test_parse_single_heading():
    # 1: Manually create the input token list
    tokens = [
        Token(TokenType.HEADING, value="My title", level=2),
        Token(TokenType.EOF)
    ]
    
    parser = Parser(tokens)
    ast = parser.parse()   # 2: Run the parser
    
    # 3: Check the structure of the resulting AST
    assert isinstance(ast, DocumentNode)
    assert len(ast.children) == 1
    
    heading_node = ast.children[0]
    assert isinstance(heading_node, HeadingNode)
    assert heading_node.text == "My title"
    assert heading_node.level == 2


def test_parse_multiple_headings():
    tokens = [
        Token(TokenType.HEADING, value="First Heading", level=1),
        Token(TokenType.HEADING, value="Second Heading", level=2),
        Token(TokenType.EOF)
    ]
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, DocumentNode)
    assert len(ast.children) == 2
    
    first_heading = ast.children[0]
    second_heading = ast.children[1]
    
    assert isinstance(first_heading, HeadingNode)
    assert first_heading.text == "First Heading"
    assert first_heading.level == 1
    
    assert isinstance(second_heading, HeadingNode)
    assert second_heading.text == "Second Heading"
    assert second_heading.level == 2


def test_parse_list_with_items():
    """
    Tests that a sequence of BULLET_ITEM tokens is parsed into a
    correct ListNode containing ListItemNodes.
    """
    # 1. Arrange: Manually create the tokens for a two-item bulleted list.
    tokens = [
        Token(TokenType.BULLET_ITEM, value="First item"),
        Token(TokenType.BULLET_ITEM, value="Second item"),
        Token(TokenType.EOF)
    ]
    parser = Parser(tokens)

    # 2. Act: Run the parser.
    ast_root = parser.parse()

    # 3. Assert: Check the structure of the resulting AST.
    
    # The document should have one child: the ListNode.
    assert len(ast_root.children) == 1
    list_node = ast_root.children[0]
    
    # Check the properties of the main list.
    assert isinstance(list_node, ListNode)
    assert list_node.list_type == "itemize"
    
    # The list should contain exactly two items.
    assert len(list_node.items) == 2
    
    # --- Check the first list item ---
    item_one = list_node.items[0]
    assert isinstance(item_one, ListItemNode)
    # The list item's content is itself a list of nodes (in this case, just one TextNode).
    assert len(item_one.children) == 1
    text_node_one = item_one.children[0]
    assert isinstance(text_node_one, TextNode)
    assert text_node_one.text == "First item"

    # --- Check the second list item ---
    item_two = list_node.items[1]
    assert isinstance(item_two, ListItemNode)
    assert len(item_two.children) == 1
    text_node_two = item_two.children[0]
    assert isinstance(text_node_two, TextNode)
    assert text_node_two.text == "Second item"