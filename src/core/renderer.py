from py_asciimath.translator.translator import ASCIIMath2Tex as AsciiMath
from pathlib import Path
from . import ast

LISTINGS_PREAMBLE = r"""
\usepackage{listings}
\usepackage{xcolor}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{black!5},
    commentstyle=\color{green!60!black},
    keywordstyle=\color{blue},
    numberstyle=\tiny\color{gray},
    stringstyle=\color{purple},
    basicstyle=\ttfamily\small,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=5pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=2,
    frame=single,
    framerule=0.2pt,
    rulecolor=\color{black!20},
}
\lstset{style=mystyle}
"""

class LatexRenderer:
    """
    Implements the Visitor pattern. It walks the AST and generates a complete
    LaTeX document string, including the preamble and metadata.
    """
    def __init__(self):
        # self.am_parser = AsciiMath(log=False, inplace=True)
        self.math_mode = 'latex'
        self.am_parser = None

    def render(self, document_node: ast.DocumentNode, metadata: dict) -> str:
        """
        The main public method. Takes the AST root and metadata, and returns
        the complete, final LaTeX document as a single string.
        """
        self.math_mode = metadata.get('math_mode', 'latex').lower()
        
        preamble = self._generate_preamble(metadata)

        # This is the main visitor entry point, which generates the document body
        body_lines = document_node.accept(self)

        # We join the body lines, preserving the blank lines from BlankLineNode
        body = "\n".join(body_lines)

        postamble = "\n\\end{document}"

        return preamble + body + postamble
    
    def _get_asciimath_parser(self):
        """
        Returns the existing AsciiMath parser instance.
        If one doesn't exist, it creates it first.
        """
        # If we haven't created the parser yet...
        if self.am_parser is None:
            print("INFO: Initializing AsciiMath translator...")
            # ...create it now and save it for future use.
            self.am_parser = AsciiMath(log=False)
        # Return the (now guaranteed to exist) parser.
        return self.am_parser

    def _generate_preamble(self, metadata: dict) -> str:
        """Generates the LaTeX preamble using the provided metadata."""
        title = metadata.get("title", "Untitled")
        author = metadata.get("author", "Unknown")
        date = metadata.get("date", "\\today")
        geometry = metadata.get("geometry")
        
        preamble_lines = [
            "\\documentclass{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{parskip}",
            "\\usepackage{graphicx}",
            "\\usepackage{amsmath}",
            "\\usepackage{booktabs}",
            "\\usepackage{float}",
            LISTINGS_PREAMBLE,
        ]
        
        if geometry:
            preamble_lines.append(f"\\usepackage[{geometry}]{{geometry}}")

            
        preamble_lines.extend([
            "\\usepackage{hyperref}",
            "\\hypersetup{",
            "    colorlinks=true,",
            "    urlcolor=blue,",
            "}",
            f"\\title{{\\textbf{{{title}}}}}",
            f"\\author{{{author}}}",
            f"\\date{{{date}}}",
            "\\begin{document}",
            "\\maketitle",
            "",  # Adds a blank line after the title block for spacing
        ])
        return "\n".join(preamble_lines) + "\n"

    def visit_document(self, node: ast.DocumentNode) -> list[str]:
        """Visits the root DocumentNode and renders all its children."""
        rendered_lines = []
        for child in node.children:
            rendered_lines.extend(child.accept(self))
        return rendered_lines

    def visit_heading(self, node: ast.HeadingNode) -> list[str]:
        if node.level == 1:
            return [f"\\section{{{node.text}}}", ""]
        elif node.level == 2:
            return [f"\\subsection{{{node.text}}}", ""]
        else:
            return [f"\\subsubsection{{{node.text}}}", ""]

    def visit_paragraph(self, node: ast.ParagraphNode) -> list[str]:
        content = "".join(child.accept(self) for child in node.children)
        return [content]

    def visit_horizontal_rule(self, node: ast.HorizontalRuleNode) -> list[str]:
        return ["\\vspace{0.3cm}", "\\noindent\\hrule", "\\vspace{0.3cm}"]

    def visit_indented_text(self, node: ast.IndentedTextNode) -> list[str]:
        return [f"\\hspace*{{2em}}{{{node.text}}}"]
    
    def visit_forced_break(self, node: ast.ForcedBreakNode) -> list[str]:
        """Renders a ForcedBreakNode into an explicit vertical space."""
        # \par ends the current paragraph, \vspace adds one line's worth of space.
        space_amount = node.num_lines
        return ["\\par\\vspace{{{}em}}".format(space_amount)]

    def visit_blank_line(self, node: ast.BlankLineNode) -> list[str]:
        """This is the key: it preserves intentional blank lines."""
        return [""]

    def visit_list(self, node: ast.ListNode) -> list[str]:
        env_name = node.list_type
        lines = [f"\\begin{{{env_name}}}"]
        for item_node in node.items:
            lines.extend(item_node.accept(self))
        lines.append(f"\\end{{{env_name}}}")
        lines.append("")  # Add a blank line after the list
        return lines

    def visit_list_item(self, node: ast.ListItemNode) -> list[str]:
        inline_parts = []
        block_lines = []
        for child in node.children:
            if isinstance(child, ast.ListNode):
                block_lines.extend(child.accept(self))
            else:
                inline_parts.append(child.accept(self))
        item_text = "".join(inline_parts)
        final_lines = [f"\\item {item_text}"]
        final_lines.extend(block_lines)
        return final_lines

    def visit_text(self, node: ast.TextNode) -> str:
        return node.text

    def visit_bold(self, node: ast.BoldNode) -> str:
        content = "".join(child.accept(self) for child in node.children)
        return f"\\textbf{{{content}}}"

    def visit_italic(self, node: ast.ItalicNode) -> str:
        content = "".join(child.accept(self) for child in node.children)
        return f"\\textit{{{content}}}"

    def visit_code(self, node: ast.CodeNode) -> str:
        escaped_text = node.text.replace('\\', '\\textbackslash{}') \
                                .replace('_', '\\_') \
                                .replace('{', '\\{') \
                                .replace('}', '\\}') \
                                .replace('^', '\\^{}') \
                                .replace('&', '\\&') \
                                .replace('%', '\\%') \
                                .replace('#', '\\#') \
                                .replace('$', '\\$')
        return "\\texttt{{{}}}".format(escaped_text)

    def visit_link(self, node: ast.LinkNode) -> str:
        content = "".join(child.accept(self) for child in node.children)
        return f"\\href{{{node.url}}}{{{content}}}"

    def visit_image(self, node: ast.ImageNode) -> list[str]:
        image_filename = Path(node.url).name
        
        # alt_text = node.alt_text
        # figure_type = "Image" #default
        # caption = alt_text
        
        # if ":" in alt_text:
        #     parts = alt_text.split(":", 1)
        #     potential_type = parts[0].strip()
        #     if potential_type:
        #         figure_type = potential_type
        #         caption = parts[1].strip()
        
        lines = [
            f"\\renewcommand{{\\figurename}}{{{node.figure_type}}}",
            "\\begin{figure}[h!]",
            "    \\centering",
            f"    \\includegraphics[width=0.8\\textwidth]{{{image_filename}}}",
            f"    \\caption{{{node.caption}}}",
            "\\end{figure}",
            "", # Add a blank line for spacing
        ]
        return lines
    
    def visit_code_block(self, node: ast.CodeBlockNode) -> list[str]:
        lines = [
            f"\\begin{{lstlisting}}[language={node.language}]",
            node.content,
            "\\end{lstlisting}",
            "", # Add a blank line for spacing
        ]
        return lines
    
    def visit_inline_math(self, node: ast.InlineMathNode) -> str:
        """Renders an InlineMathNode into $...$"""
        if self.math_mode == 'asciimath':
            parser = self._get_asciimath_parser()
            return parser.translate(node.content) or ""
        else:
            return f"${node.content}$"

    def visit_block_math(self, node: ast.BlockMathNode) -> list[str]:
        """Renders a BlockMathNode into a LaTeX block math environment."""
        if self.math_mode == 'asciimath':
            parser = self._get_asciimath_parser()
            content = parser.translate(node.content, displaystyle=True) or ""
            return [content, ""]
        else:
            lines = [
                "\\begin{equation*}",
                node.content,
                "\\end{equation*}",
                "",
            ]
            return lines

    def visit_table(self, node: ast.TableNode) -> list[str]:
        if not node.headers:
            return []
            
        num_columns = len(node.headers)
        latex_align = "|" + "|".join(['l'] * num_columns) + "|"
        
        lines = ["\\begin{table}[H]"]
            
        lines.extend([
            "   \\centering", 
            "   \\small",
            "   \\begin{{tabular}}{{{}}}".format(latex_align),
            "   \\toprule"
        ])
        
        lines.append("   {} \\\\".format(' & '.join([f'\\textbf{{{h}}}' for h in node.headers])))
        lines.append("   \\midrule")
        
        for row in node.rows:
            lines.append("   {} \\\\".format(' & '.join(row)))
        
        lines.extend([
            "   \\bottomrule", 
            "   \\end{tabular}",
        ])
        
        if node.caption: 
            lines.append("   \\caption{{{}}}".format(node.caption))
            
        lines.extend([
            "\\end{table}",
            ""
        ])
        
        return lines