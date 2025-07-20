from typing import Optional
from pathlib import Path
from src.pipeline.config import PipelineConfig
from src.pipeline.builder import PipelineBuilder


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
        print(f"✅ Successfully processed {self.config.input_path}")
        if self.config.generate_pdf and result:
            print(f"📤 Final PDF output written to {result}")
    
    def _handle_error(self, error: Exception) -> None:
        """Handle execution errors."""
        print(f"🚨 Error: {error}")
        exit(1)