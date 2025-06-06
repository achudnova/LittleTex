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

# extract fields from the markdown file
def extract_metadata(markdown_content: str) -> tuple[dict, str]:
    """Extract metadata from markdown content.

    Args:
        markdown_content (str): Raw markdown content as a string

    Returns:
        tuple[dict, str]: (metadata dict, content without metadata)
    """
    metadata = {}
    lines = markdown_content.split("\n")
    metadata_lines = []
    
    # process lines that start with @ as metadata
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith("@"):
            try:
                metadata_lines.append(i)
                key, value = line_stripped[1:].split(":", 1)
                metadata[key.strip()] = value.strip()
                content_start = i + 1
            except ValueError:
                break
        elif i > 0 and not line_stripped:
            continue
        else:
            break
    
    content_lines = [line for i, line in enumerate(lines) if i not in metadata_lines]
    content_without_metadata = "\n".join(content_lines)
    return metadata, content_without_metadata