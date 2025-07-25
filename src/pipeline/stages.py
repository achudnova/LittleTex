import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .core import Stage
from src.core.ast import DocumentNode, ImageNode
from src.core.tokenizer import Tokenizer, Token
from src.core.parser import Parser
from src.core.renderer import LatexRenderer
from src.utils.text_processing import extract_metadata
from src.utils.pdf_generator import generate_pdf_from_latex


class ReadFileStage(Stage):
    def __init__(self, path: Path):
        self.path = path
    
    def run(self, _: Any) -> str:
        """Read the entire markdown file as a string."""
        return self.path.read_text(encoding="utf-8")


class MetadataStage(Stage):
    def run(self, content: str) -> Tuple[Dict[str, str], str]:
        """Extract metadata and return (metadata, clean_markdown)"""
        return extract_metadata(content)


class TokenizeStage(Stage):
    def run(self, data: Tuple[Dict[str, str], str]) -> Tuple[Dict[str, str], List[Token]]:
        """Tokenize the markdown into a list of tokens."""
        metadata, markdown = data
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(markdown)
        return metadata, tokens


class ParseStage(Stage):
    def run(self, data: Tuple[Dict[str, str], List[Token]]) -> Tuple[Dict[str, str], DocumentNode]:
        """Parse tokens into an AST."""
        metadata, tokens = data
        parser = Parser(tokens)
        ast = parser.parse()
        return metadata, ast    


class RenderStage(Stage):
    def __init__(self):
        self.renderer = LatexRenderer()
    
    def run(self, data: Tuple[Dict[str, str], DocumentNode]) -> Tuple[Dict[str, str], str]:
        """Render the AST and metadata to a LaTeX string."""
        metadata, ast = data
        latex_document = self.renderer.render(ast, metadata)
        return metadata, latex_document


class WriteFileStage(Stage):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self, data: Tuple[Dict[str, str], str]) -> Path:
        """Write the LaTex string to a .tex file. Returns its path."""
        metadata, tex_content = data
        title = metadata.get("title", "output")
        tex_path = self.output_dir / f"{title}.tex"
        tex_path.write_text(tex_content, encoding="utf-8")
        print(f"📝 LaTeX document written to {tex_path}")
        return tex_path


class PdfStage(Stage):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        
    def run(self, tex_path: Path) -> Path:
        """Compile the .tex file file into a PDF and return its path."""
        success, pdf_path_or_error = generate_pdf_from_latex(tex_path)
        if not success:
            raise RuntimeError(f"Failed to generate PDF: {pdf_path_or_error}")
        
        # pdf_path_or_error is now the actual path when success is True
        pdf_path = Path(pdf_path_or_error) if pdf_path_or_error else tex_path.with_suffix('.pdf')
        return pdf_path
        

class CopyAssetsStage(Stage):
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self, data: Tuple[Dict[str, str], DocumentNode]) -> Tuple[Dict[str, str], DocumentNode]:
        """
        Scans the AST for image nodes and copies the image files to the output directory.
        """
        metadata, ast_root = data
        self._find_and_copy_images(ast_root)
        # Pass the data through to the next stage unmodified.
        return metadata, ast_root

    def _find_and_copy_images(self, node: Any):
        """Recursively traverses the AST to find and copy images."""
        if isinstance(node, DocumentNode):
            for child in node.children:
                self._find_and_copy_images(child)
        elif hasattr(node, "children"):
            for child in node.children:
                self._find_and_copy_images(child)
        elif isinstance(node, ImageNode):
            # We have an image. Construct the source path and copy it.
            source_path = self.input_dir / node.url
            dest_path = self.output_dir / Path(node.url).name

            if source_path.resolve() != dest_path.resolve():
                if source_path.is_file():
                    print(f"> Copying asset: {source_path} to {dest_path}")
                    shutil.copy(source_path, dest_path)
                else:
                    print(f"Warning: Image file not found at {source_path}")
            else:
                print(f"> Asset already in destination, skipping copy: {source_path}")