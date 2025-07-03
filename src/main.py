import argparse
from pathlib import Path
from src.core.pipeline import (
    Pipeline, ReadFileStage, MetadataStage, TokenizeStage,
    ParseStage, RenderStage, WriteFileStage, PdfStage
)

def run_app() -> None:
    """Entry point for the littletex command using pipeline architecture."""
    parser = argparse.ArgumentParser(description="Converts Markdown to LaTeX.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("output_file", help="Path to the output LaTeX file.")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF from LaTeX.")
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)
    output_dir = output_path.parent
    
    stages = [
        ReadFileStage(input_path),
        MetadataStage(),
        TokenizeStage(),
        ParseStage(),
        RenderStage(),
        WriteFileStage(output_dir),
        #PdfStage(output_dir),
        
    ]
    if args.pdf:
        stages.append(PdfStage(output_dir))

    pipeline = Pipeline(stages)
    pipeline.execute()
    

if __name__ == "__main__":
    run_app()
