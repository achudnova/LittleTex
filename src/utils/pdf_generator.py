import subprocess
import os
from typing import Optional, Tuple

def generate_pdf_from_latex(tex_file: str) -> Tuple[bool, Optional[str]]:
    """Converts a .tex file to PDF using pdflatex

    Args:
        tex_file (str): path to the .tex file

    Returns:
        Tuple[bool, Optional[str]]: (success, pdf_path_or_error_message)
    """
    
    if not os.path.exists(tex_file):
        return False, f"Error: File not found {tex_file}"
    
    tex_dir = os.path.dirname(tex_file) or "."
    base_name = os.path.basename(tex_file)
    
    try:
        check_cmd = subprocess.run(
            ["which", "pdflatex"],
            capture_output=True,
            text=True
        )
        if check_cmd.returncode != 0:
            return False, "Error: pdflatex is not installed or not found in PATH."
        
        print(f"Generating PDF from {tex_file}...")
        
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", base_name],
            cwd=tex_dir,
            capture_output=True,
            text=True
        )
        
        # get the pdf filename
        pdf_file = os.path.splitext(base_name)[0] + ".pdf"
        pdf_path = os.path.join(tex_dir, pdf_file)
        
        aux_extensions = [".aux", ".log", ".out"]
        for ext in aux_extensions:
            aux_file = os.path.splitext(base_name)[0] + ext
            aux_path = os.path.join(tex_dir, aux_file)
            if os.path.exists(aux_path):
                try:
                    os.remove(aux_path)
                except PermissionError:
                    print(f"Warning: Could not delete auxiliary file {aux_file}. It may be in use.")
        
        if result.returncode == 0 and os.path.exists(pdf_path):
            print(f"> PDF successfully generated: {pdf_path}")
            return True, None
        else:
            error_msg = result.stderr if result.stderr else "Unknown error (check if pdflatex ran correctly)"
            return False, f"Error generating PDF: {error_msg}"
    
    except Exception as e:
        return False, f"Error running pdflatex: {str(e)}"