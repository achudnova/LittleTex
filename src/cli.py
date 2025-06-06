# handles the command line part
# responsible for understand the filenames you type in the terminal (input_name.md, output_name.tex)
# calls the render_text_to_latex() function to get the LaTeX String
# writing the LaTeX String into the output file you specified

from typing import List
import argparse # helps read command-line arguments
from src.core.renderer import render_text_to_latex
from src.core.parser import parse_markdown_to_latex, extract_metadata
from src.utils.pdf_generator import generate_pdf_from_latex

def main_cli() -> None:
    # 1. Setup to understand command-line arguments
    parser = argparse.ArgumentParser(description="Converts Markdown to LaTeX.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("output_file", help="Path to the output LaTeX file.")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF from LaTeX.")
    
    # 2. Read the arguments typed by the user
    args: argparse.Namespace = parser.parse_args()
    
    input_file: str = args.input_file
    output_file: str = args.output_file
    generate_pdf: bool = args.pdf
    
    # print what we received, just for checking
    print(f"Input file specified: {input_file}")
    print(f"Output file specified: {output_file}")
    
    # 1. Read the content from Markdown file
    markdown_content: str = ""
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            markdown_content = f_in.read() # Read the whole file into one string
        
        metadata, content_without_metadata = extract_metadata(markdown_content)
        # parsed_latex_lines: List[str] = parse_markdown_to_latex(content_without_metadata)
        
        # latex_document: str = render_text_to_latex(
        #     parsed_latex_lines,
        #     title=metadata.get('title', 'Untitled'),
        #     author=metadata.get('author', 'Unknown'),
        # )
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except IOError as e:
        print(f"Error reading input file: {e}")
        return
    
    # 2. Parse the Markdown content into LaTeX lines
    parsed_latex_lines: List[str] = parse_markdown_to_latex(content_without_metadata)
    
    # 3. Render the full .tex document 
    latex_document: str = render_text_to_latex(
        parsed_latex_lines,
        title=metadata.get('title', 'Untitled'),
        author=metadata.get('author', 'Unknown'),
        date=metadata.get('date', '\\today')  # Use today's date if not specified
    )
    
    # 3. Prepare placeholder content for the renderer
    # placeholder_content: List[str] = [
    #     "% This is where real content will go in future steps.\n",
    #     "Hello from LittleTex MVP!\n"
    # ]
    
    # 4. Call the renderer to get the full LaTeX document string
    # latex_content: str = render_text_to_latex(placeholder_content)
    
    # 4. Write the LaTeX string to the output file
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(latex_document)
            print(f"LaTeX content written to {args.output_file}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        
    # 5. Generate pdf if requested
    if generate_pdf:
        success, error = generate_pdf_from_latex(output_file)
        if not success:
            print(error)
        
if __name__ == "__main__":
    main_cli()