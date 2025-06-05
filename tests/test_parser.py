import pytest
from typing import List
from src.core.parser import parse_markdown_to_latex

def test_h1_heading():
    markdown_input: str = "# Heading 1"
    expected_latex: List[str] = ["\\section{Heading 1}"]
    actual_latex_output: List[str] = parse_markdown_to_latex(markdown_input)
    assert actual_latex_output == expected_latex