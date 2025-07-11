from abc import ABC, abstractmethod
from typing import Any, List


class Stage(ABC):
    """A processing stage takes an input, does work, and returns an output for the next stage."""
    
    @abstractmethod
    def run(self, data: Any) -> Any:
        pass

class Pipeline:
    def __init__(self, stages: List[Stage]):
        self.stages = stages
    
    def execute(self, input_data: Any = None) -> Any:
        """Run the pipeline through all stages."""
        result = input_data
        for stage in self.stages:
            result = stage.run(result)
        return result