# handles the command line part
# responsible for understand the filenames you type in the terminal (input_name.md, output_name.tex)
# calls the render_text_to_latex() function to get the LaTeX String
# writing the LaTeX String into the output file you specified

import argparse # helps read command-line arguments
from src.core.renderer import render_text_to_latex
from typing import List

def main_cli() -> None:
    # 1. Setup to understand command-line arguments
    parser = argparse.ArgumentParser(description="Converts Markdown to LaTeX.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("output_file", help="Path to the output LaTeX file.")
    
    # 2. Read the arguments typed by the user
    args = parser.parse_args()
    
    input_file: str = args.input_file
    output_file: str = args.output_file
    
    # print what we received, just for checking
    print(f"Step 1: Input file specified: {input_file}")
    print(f"Step 2: Output file specified: {output_file}")
    
    # 3. Prepare placeholder content for the renderer
    placeholder_content: List[str] = [
        "% This is where real content will go in future steps.\n",
        "Hello from LittleTex MVP!\n"
    ]
    
    # 4. Call the renderer to get the full LaTeX document string
    latex_content: str = render_text_to_latex(placeholder_content)
    
    # 5. Write the LaTeX string to the output file
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(latex_content)
            print(f"Step 3: LaTeX content written to {args.output_file}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        
if __name__ == "__main__":
    main_cli()