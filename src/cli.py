import argparse
from typing import List

from src.core.tokenizer import Tokenizer
from src.core.parser import Parser, extract_metadata
from src.core.renderer import LatexRenderer

# from src.core.renderer_copy import render_text_to_latex
from src.utils.pdf_generator import generate_pdf_from_latex

def main_cli() -> None:
    # 1. Setup and read command line arguments
    parser = argparse.ArgumentParser(description="Converts Markdown to LaTeX.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("output_file", help="Path to the output LaTeX file.")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF from LaTeX.")
    args: argparse.Namespace = parser.parse_args()
    
    input_file: str = args.input_file
    output_file: str = args.output_file
    generate_pdf: bool = args.pdf
    
    print(f"Input file specified: {input_file}")
    print(f"Output file specified: {output_file}")
    
    # 2. Read the content from the Markdown file
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            markdown_content = f_in.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except IOError as e:
        print(f"Error reading input file: {e}")
        return
    
    # 3. Extract metadata from the raw content
    metadata, content_without_metadata = extract_metadata(markdown_content)
    
    # 4. Stage 1: Tokezine the content
    tokenizer = Tokenizer()
    tokens: List = tokenizer.tokenize(content_without_metadata)
    
    # 5. Stage 2: Parse the tokens into an AST
    parser = Parser(tokens)
    ast_document = parser.parse()
    
    # 6. Stage 3: Render the AST into a LaTeX string (document body)
    latex_renderer = LatexRenderer()
    latex_document: str = latex_renderer.render(ast_document, metadata)
    
    # 7. Use the old renderer to warp the body with the document preamble
    # latex_document: str = render_text_to_latex(
    #     content_lines=latex_body_content.splitlines(),
    #     title=metadata.get('title', 'Unknown'),
    #     author=metadata.get('author', 'Unknown'),
    #     date=metadata.get('date', '\\today')
    # )
    
    # 8. Write the LaTeX string to the output file
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(latex_document)
            print(f"LaTeX document written to {args.output_file}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        
    # 9. Generate PDF if requested
    if generate_pdf:
        success, error = generate_pdf_from_latex(output_file)
        if not success:
            print(error)

if __name__ == "__main__":
    main_cli()