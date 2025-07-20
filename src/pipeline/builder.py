"""Pipeline construction logic."""

from src.pipeline.config import PipelineConfig
from .core import Pipeline
from .stages import (
    ReadFileStage,
    MetadataStage,
    TokenizeStage,
    ParseStage,
    RenderStage,
    WriteFileStage,
    PdfStage,
    CopyAssetsStage,
)


class PipelineBuilder:
    """Builder for creating processing pipelines."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.stages = []
    
    def add_core_stages(self) -> "PipelineBuilder":
        """Add the core processing stages"""
        input_dir = self.config.input_path.parent
        
        self.stages.extend([
            ReadFileStage(self.config.input_path),
            MetadataStage(),
            TokenizeStage(),
            ParseStage(),
            CopyAssetsStage(input_dir, self.config.output_dir),
            RenderStage(),
            WriteFileStage(self.config.output_dir),
        ])
        return self
    
    def add_pdf_stage_if_needed(self) -> "PipelineBuilder":
        """Add PDF generation stage if requested."""
        if self.config.generate_pdf:
            self.stages.append(PdfStage(self.config.output_dir))
        return self
    
    def build(self) -> Pipeline:
        """Build the configured pipeline."""
        return Pipeline(self.stages)

