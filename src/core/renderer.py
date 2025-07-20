from pathlib import Path
from . import ast


class LatexRenderer:
    """
    Implements the Visitor pattern. It walks the AST and generates a complete
    LaTeX document string, including the preamble and metadata.
    """

    def render(self, document_node: ast.DocumentNode, metadata: dict) -> str:
        """
        The main public method. Takes the AST root and metadata, and returns
        the complete, final LaTeX document as a single string.
        """
        preamble = self._generate_preamble(metadata)

        # This is the main visitor entry point, which generates the document body
        body_lines = document_node.accept(self)

        # We join the body lines, preserving the blank lines from BlankLineNode
        body = "\n".join(body_lines)

        postamble = "\n\\end{document}"

        return preamble + body + postamble

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
            "\\renewcommand{\\figurename}{Image}", # TODO
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
        return f"\\texttt{{{node.text}}}"

    def visit_link(self, node: ast.LinkNode) -> str:
        content = "".join(child.accept(self) for child in node.children)
        return f"\\href{{{node.url}}}{{{content}}}"

    def visit_image(self, node: ast.ImageNode) -> list[str]:
        image_filename = Path(node.url).name
        lines = [
            "\\begin{figure}[h!]",
            "    \\centering",
            f"    \\includegraphics[width=0.8\\textwidth]{{{image_filename}}}",
            f"    \\caption{{{node.alt_text}}}",
            "\\end{figure}",
            "", # Add a blank line for spacing
        ]
        return lines