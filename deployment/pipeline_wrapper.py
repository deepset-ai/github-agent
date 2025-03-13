from pathlib import Path
from typing import Generator, List, Union
from haystack import Pipeline
from hayhooks import get_last_user_message, BasePipelineWrapper, log
from agent_pipeline.agent_pipeline import agent_pipe

class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        self.pipeline = agent_pipe()

    def run_api(self, url: str) -> str:
        log.trace(f"Running pipeline with urls: {url}")
        result = self.pipeline.run({"url": url})
        return result
