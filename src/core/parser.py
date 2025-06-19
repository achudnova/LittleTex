# logic to look at each markdown line and decide how to convert it to LaTeX

from typing import List, Dict
import re

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
    in_bullet_list: bool = False
    in_numbered_list: bool = False
    
    for line in markdown_lines:
        stripped_line: str = line.strip() # Remove leading/trailing whitespace for checking
        
        if stripped_line.startswith("- "):
            if not in_bullet_list:
                # close numbered list if open
                if in_numbered_list:
                    latex_output_lines.append("\\end{enumerate}")
                    in_numbered_list = False
                    
                # start bullet list
                latex_output_lines.append("\\begin{itemize}")
                in_bullet_list = True
            
            item_content = format_inline_elements(stripped_line[2:])  # Get text after "- "
            latex_output_lines.append(f"\\item {item_content}")
            previous_line_was_blank = False
            continue
        
        numbered_list_match = re.match(r'^\d+\.\s+(.*)', stripped_line)
        if numbered_list_match:
            if not in_numbered_list:
                if in_bullet_list:
                    latex_output_lines.append("\\end{itemize}")
                    in_bullet_list = False
                latex_output_lines.append("\\begin{enumerate}")
                in_numbered_list = True
            
            item_content = format_inline_elements(numbered_list_match.group(1))
            latex_output_lines.append(f"\\item {item_content}")
            previous_line_was_blank = False
            continue
        
        if in_bullet_list and not stripped_line.startswith("- "):
            # End of bullet list if the next line is not a bullet point
            latex_output_lines.append("\\end{itemize}")
            in_bullet_list = False
        
        if in_numbered_list and not re.match(r'^\d+\.\s+', stripped_line):
            # End of numbered list if the next line is not a numbered point
            latex_output_lines.append("\\end{enumerate}")
            in_numbered_list = False
        
        if stripped_line == "---":
            # Horizontal rule
            latex_output_lines.append("\\vspace{0.3cm}")
            latex_output_lines.append("\\noindent\\hrule")
            latex_output_lines.append("\\vspace{0.3cm}")
            previous_line_was_blank = False
            continue
        
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