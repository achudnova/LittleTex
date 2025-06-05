# logic to look at each markdown line and decide how to convert it to LaTeX

from typing import List

def parse_markdown_to_latex(markdown_content: str) -> List[str]:
    """Parses a string containing multiple lines of Markdown content.
    Args:
        markdown_lines (str): string containing all lines of the Markdown file

    Returns:
        List[str]: A list of strings, where each string is a line of LaTeX
    """
    
    markdown_lines: List[str] = markdown_content.splitlines() # Split the input string into individual lines
    latex_output_lines: List[str] = []
    previous_line_was_blank: bool = False
    
    for line in markdown_lines:
        stripped_line: str = line.strip() # Remove leading/trailing whitespace for checking
        
        if stripped_line.startswith("# "):
            # Level 1 heading (section)
            heading_text: str = stripped_line[2:] # get text after ## 
            latex_output_lines.append(f"\\section{{{heading_text}}}")
            previous_line_was_blank: bool = False
            
        elif stripped_line.startswith("## "):
            # Level 2 heading (subsection)
            heading_text: str = stripped_line[3:]
            latex_output_lines.append(f"\\subsection{{{heading_text}}}")
            previous_line_was_blank: bool = False
        
        elif stripped_line.startswith("### "):
            heading_text: str = stripped_line[4:]
            latex_output_lines.append(f"\\subsubsection{{{heading_text}}}")
            previous_line_was_blank: bool = False
        
        elif stripped_line.startswith(">> "):
            heading_text: str = stripped_line[3:]
            latex_output_lines.append(f"\\hspace*{{2em}}{{{heading_text}}}")
            previous_line_was_blank: bool = False
            
        elif stripped_line: # line has content and is not empty
            latex_output_lines.append(line + "\n")
            previous_line_was_blank: bool = False
            
        else: # empty line
            if not previous_line_was_blank:
                latex_output_lines.append("")
            previous_line_was_blank = True
    
    return latex_output_lines
