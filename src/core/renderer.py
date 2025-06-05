# generate text as a Python string

from typing import List

def render_text_to_latex(content_lines: List[str]) -> str:
    """Takes a list of lines (meant to be LaTeX later) and wraps them
    in a standard LaTeX document structure.

    Args:
        content_lines (list[str]): A list of strings, where each string is expected
            to be a line of LaTeX code.
    Returns:
        str: A string containing the complete LaTeX document.
    """
    
    latex_output: List[str] = [] # holds list of strings
    
    # 1. LaTeX Preamble
    latex_output.append("\\documentclass{article}\n")
    latex_output.append("\\usepackage[utf8]{inputenc}\n")
    latex_output.append("\\title{Generated Document}\n")
    latex_output.append("\\author{LittleTex Tool}\n")
    latex_output.append("\\date{\\today}\n")
    
    # 2. Start of the document body
    latex_output.append("\\begin{document}\n")
    latex_output.append("\\maketitle\n")
    
    # 3. The actual content
    latex_output.append("\n")
    if not content_lines:
        latex_output.append("No content provided.\n")
    else:
        for line in content_lines:
            latex_output.append(line + "\n")
    
    # 4. End of the document body
    latex_output.append("\\end{document}\n")
    
    return "".join(latex_output)