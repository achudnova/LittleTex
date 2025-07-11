"""Pipeline construction logic."""

from typing import List
from src.config.pipeline_config import PipelineConfig
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

