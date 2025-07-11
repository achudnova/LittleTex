
from pathlib import Path
from typing import List, Optional
from src.core.pipeline import (
    Pipeline,
    Stage,
    ReadFileStage,
    MetadataStage,
    TokenizeStage,
    ParseStage,
    RenderStage,
    WriteFileStage,
    PdfStage,
)
from src.cli.argument_parser import ArgumentParser
from src.config.pipeline_config import PipelineConfig

class PipelineBuilder:
    """Builder for creating processing pipelines."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self._stages: List[Stage] = []
    
    def add_core_stages(self) -> "PipelineBuilder":
        """Add the core processing stages"""
        self._stages.extend([
            ReadFileStage(self.config.input_path),
            MetadataStage(),
            TokenizeStage(),
            ParseStage(),
            RenderStage(),
            WriteFileStage(self.config.output_dir),
        ])
        return self
    
    def add_pdf_stage_if_needed(self) -> "PipelineBuilder":
        """Add PDF generation stage if requested."""
        if self.config.generate_pdf:
            self._stages.append(PdfStage(self.config.output_dir))
        return self
    
    def build(self) -> Pipeline:
        """Build the configured pipeline."""
        return Pipeline(self._stages)





class LittleTexApp:
    """Main application orchestrator."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        
    def run(self) -> None:
        """Execute the conversion process."""
        pipeline = (PipelineBuilder(self.config)
                    .add_core_stages() 
                    .add_pdf_stage_if_needed() 
                    .build())
        try:
            result = pipeline.execute()
            self._print_success_message(result)
        except Exception as e:
            self._handle_error(e)
    
    def _print_success_message(self, result: Optional[Path]) -> None:
        """Print success message based on execution result."""
        print(f"Successfully processed {self.config.input_path}")
        if self.config.generate_pdf and result:
            print(f"Final output written to {result}")
    
    def _handle_error(self, error: Exception) -> None:
        """Handle execution errors."""
        print(f"Error: {error}")
        exit(1)


def run_app() -> None:
    """Entry point for the littletex command."""
    config = ArgumentParser.parse_args()
    app = LittleTexApp(config)
    app.run()



if __name__ == "__main__":
    run_app()
