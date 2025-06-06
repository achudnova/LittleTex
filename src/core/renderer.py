# generate text as a Python string

from typing import List


def render_text_to_latex(
    content_lines: List[str],
    title: str = "Unknown",
    author: str = "Unknown",
    date: str = "\\today",
) -> str:
    """Takes a list of lines (meant to be LaTeX later) and wraps them
    in a standard LaTeX document structure.

    Args:
        content_lines (list[str]): A list of strings, where each string is expected
            to be a line of LaTeX code.
    Returns:
        str: A string containing the complete LaTeX document.
    """

    latex_output: List[str] = []  # holds list of strings

    # 1. LaTeX Preamble
    latex_output.append("\\documentclass{article}\n")
    latex_output.append("\\usepackage[utf8]{inputenc}\n")
    latex_output.append("\\usepackage{parskip}\n")
    latex_output.append(f"\\title{{\\textbf{{{title}}}}}\n")
    latex_output.append(f"\\author{{{author}}}\n")
    # latex_output.append("\\date{\\today}\n")
    
    if date == "\\today":
        latex_output.append("\\date{\\today}\n")
    else:
        latex_output.append(f"\\date{{{date}}}\n")

    # 2. Start of the document body
    latex_output.append("\\begin{document}\n")
    latex_output.append("\\maketitle\n")

    # if content_lines:
    #     latex_output.append("\n")

    # for line in content_lines:
    #     latex_output.append(line)

    # if content_lines:
    #     latex_output.append("\n")

    # 3. The actual content
    latex_output.append("\n")
    if not content_lines:
        latex_output.append("No content provided.\n")
    else:
        for line in content_lines:
            latex_output.append(line)
            if line != "":
                latex_output.append("\n")

    # 4. End of the document body
    latex_output.append("\\end{document}\n")

    return "".join(latex_output)
