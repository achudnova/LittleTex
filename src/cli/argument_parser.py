import argparse
from pathlib import Path
from src.config.pipeline_config import PipelineConfig


class ArgumentParser:
    """Handles command line argument parsing."""
    
    @staticmethod
    def parse_args() -> PipelineConfig:
        """Parse command line arguments and return configuration."""
        parser = argparse.ArgumentParser(description="Converts Markdown to LaTeX.")
        parser.add_argument("input_file", help="Path to the input Markdown file.")
        parser.add_argument("output_file", help="Path to the output LaTeX file.")
        parser.add_argument("--pdf", action="store_true", help="Generate PDF from LaTeX.")
        
        args = parser.parse_args()
        
        return PipelineConfig(
            input_path=Path(args.input_file),
            output_path=Path(args.output_file),
            generate_pdf=args.pdf  
        )