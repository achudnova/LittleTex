from . import ast

class LatexRenderer:
    """implements visitor pattern, walks the AST and generates a list of LaTeX strings"""
    
    def render(self, document_node: ast.DocumentNode) -> str:
        """takes a DocumentNode and returns a string containing the LaTeX code"""
        lines = document_node.accept(self)
        return "\n".join(lines)
    
    def visit_document(self, node: ast.DocumentNode) -> list[str]:
        """visits the root DocumentNode"""
        rendered_lines = []
        for child in node.children:
            rendered_lines.extend(child.accept(self))
        return rendered_lines
    
    def visit_heading(self, node: ast.HeadingNode) -> list[str]:
        """visits a HeadingNode and returns LaTeX code for it"""
        if node.level == 1:
            return [f"\\section{{{node.text}}}"]
        elif node.level == 2:
            return [f"\\subsection{{{node.text}}}"]
        elif node.level == 3:
            return [f"\\subsubsection{{{node.text}}}"]
    
    def visit_paragraph(self, node: ast.ParagraphNode) -> list[str]:
        """translates a ParagraphNode into plain text with a newline"""
        content = "".join(child.accept(self) for child in node.children)
        return [content, ""]
    
    def visit_horizontal_rule(self, node: ast.HorizontalRuleNode) -> list[str]:
        """translates a HorizontalRuleNode into a LaTeX hrule"""
        return ["\\vspace{0.3cm}", "\\noindent\\hrule", "\\vspace{0.3cm}"]

    def visit_indented_text(self, node: ast.IndentedTextNode) -> list[str]:
        """translates an IndentedTextNode"""
        return [f"\\hspace*{{2em}}{{{node.text}}}"]
    
    def visit_blank_line(self, node: ast.BlankLineNode) -> list[str]:
        """translates a BlankLineNode into an empty string"""
        return [""]
    
    def visit_list(self, node: ast.ListNode) -> list[str]:
        """visits a ListNode. This method is responsible for creating the 'begin' and 'end' environment for the list"""
        # 1. get the correct name (itemize or enumerate) from the node's list_type
        env_name = node.list_type
        
        # 2. start the list with the begin command
        lines = [f"\\begin{{{env_name}}}"]
        
        # 3. visit each item in the list
        for item_node in node.items:
            lines.extend(item_node.accept(self))
            
        # 4. close the list with the end command
        lines.append(f"\\end{{{env_name}}}")
        return lines
    
    def visit_list_item(self, node: ast.ListItemNode) -> list[str]:
        """visits a ListItemNode and renders the content inside a single list item"""
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
        """Renders plain text."""
        return node.text
    
    def visit_bold(self, node: ast.BoldNode) -> str:
        """Renders bold text."""
        content = "".join(child.accept(self) for child in node.children)
        return f"\\textbf{{{content}}}"
    
    def visit_italic(self, node: ast.ItalicNode) -> str:
        """Renders italic text."""
        content = "".join(child.accept(self) for child in node.children)
        return f"\\textit{{{content}}}"

    def visit_code(self, node: ast.CodeNode) -> str:
        """Renders inline code."""
        return f"\\texttt{{{node.text}}}"

    def visit_link(self, node: ast.LinkNode) -> str:
        """Renders a hyperlink. Requires the 'hyperref' package."""
        content = "".join(child.accept(self) for child in node.children)
        return f"\\href{{{node.url}}}{{{content}}}"