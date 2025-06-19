# logic to look at each markdown line and decide how to convert it to LaTeX

from typing import List, Dict, Tuple
import re

def get_indentation(line: str) -> int:
    """Calculates the indentation of a line."""
    return len(line) - len(line.lstrip(' '))

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
    
    list_stack: List[Tuple[str, int]] = []
    
    for line in markdown_lines:
        stripped_line: str = line.strip() # Remove leading/trailing whitespace for checking
        indentation = get_indentation(line)
        
        is_bullet_item = stripped_line.startswith("- ")
        numbered_list_match = re.match(r'^\d+\.\s+(.*)', stripped_line)
        is_numbered_item = numbered_list_match is not None
        is_list_item = is_bullet_item or is_numbered_item
        
        if is_list_item:
            current_list_type = "itemize" if is_bullet_item else "enumerate"
            
            while list_stack and indentation < list_stack[-1][1]:
                closed_type, _ = list_stack.pop()
                latex_output_lines.append(f"\\end{{{closed_type}}}")
            
            if list_stack and indentation == list_stack[-1][1] and current_list_type != list_stack[-1][0]:
                closed_type, _ = list_stack.pop()
                latex_output_lines.append(f"\\end{{{closed_type}}}")
            
            if not list_stack or current_list_type != list_stack[-1][0] or indentation > list_stack[-1][1]:
                latex_output_lines.append(f"\\begin{{{current_list_type}}}")
                list_stack.append((current_list_type, indentation))
            
            item_content_raw = stripped_line[2:] if is_bullet_item else numbered_list_match.group(1)
            item_content = format_inline_elements(item_content_raw)
            latex_output_lines.append(f"\\item {item_content}")
            previous_line_was_blank = False
        
        else:
            while list_stack:
                closed_type, _ = list_stack.pop()
                latex_output_lines.append(f"\\end{{{closed_type}}}")
            
            if stripped_line == "---":
                # Horizontal rule
                latex_output_lines.append("\\vspace{0.3cm}")
                latex_output_lines.append("\\noindent\\hrule")
                latex_output_lines.append("\\vspace{0.3cm}")
                previous_line_was_blank = False
                #continue
            
            elif stripped_line.startswith("# "):
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
                formatted_line: str = format_inline_elements(line)  # Convert inline elements
                latex_output_lines.append(formatted_line + "\n") #line + "\n"
                previous_line_was_blank: bool = False
                
            else: # empty line
                if not previous_line_was_blank:
                    latex_output_lines.append("")
                previous_line_was_blank = True
    
    while list_stack:
        closed_type, _ = list_stack.pop()
        latex_output_lines.append(f"\\end{{{closed_type}}}")
    
    return latex_output_lines

# extract fields from the markdown file
def extract_metadata(markdown_content: str) -> tuple[dict, str]:
    """Extract metadata from markdown content.

    Args:
        markdown_content (str): Raw markdown content as a string

    Returns:
        tuple[dict, str]: (metadata dict, content without metadata)
    """
    metadata: Dict[str, str] = {}
    lines = markdown_content.split("\n")
    metadata_lines: List[str] = []
    
    # process lines that start with @ as metadata
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith("@"):
            metadata_lines.append(i)
            if line_stripped == "@datetoday":
                metadata["date"] = "\\today"
            elif ":" in line_stripped:
                try:
                    key, value = line_stripped[1:].split(":", 1)
                    metadata[key.strip()] = value.strip()
                except ValueError:
                    pass
        elif i > 0 and not line_stripped:
            continue
        else:
            break
    
    content_lines = [line for i, line in enumerate(lines) if i not in metadata_lines]
    content_without_metadata = "\n".join(content_lines)
    return metadata, content_without_metadata

def format_inline_elements(text: str) -> str:
    """Convert Markdown inline formatting to LaTeX.
    Converts inline elements like bold, italic, and code to LaTeX format.

    Args:
        text (str): Text with potential Markdown formatting

    Returns:
        str: Text with LaTeX formatting commands
    """
    # Bold: **text** -> \textbf{text}
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    
    # Intalic: *text* -> \textit{text}
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)  # Italic: *text* -> \textit{text}
    
    # Code: `code` -> \texttt{code}
    text = re.sub(r'`(.*?)`', r'\\texttt{\1}', text)
    
    # Links: [text](url) -> \href{url}{text}
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    
    
    return text