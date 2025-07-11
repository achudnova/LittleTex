from pathlib import Path

class PipelineConfig:
    """Configuration for pipeline execution."""

    def __init__(self, input_path: Path, output_path: Path, generate_pdf: bool = False):
        self.input_path = input_path            # path to the input Markdown file
        self.output_path = output_path          # path to the output LaTeX file
        self.output_dir = (output_path.parent)  # directory where the output file will be saved
        self.generate_pdf = generate_pdf        # whether to generate PDF from LaTeX

