import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '')))

# Now import from src
from src.agent_pipeline import agent_pipe

# Define the pipeline function that Hayhooks will use
def pipeline():
    return agent_pipe()

from src.agent_pipeline import agent_pipe
from pathlib import Path
from typing import Generator, List, Union
from haystack import Pipeline
from hayhooks import get_last_user_message, BasePipelineWrapper, log
from src.agent_pipeline import agent_pipe

class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        self.pipeline = agent_pipe()

    def run_api(self, url: str) -> str:
        log.trace(f"Running pipeline with urls: {url}")
        result = self.pipeline.run({"url": url})
        return result
