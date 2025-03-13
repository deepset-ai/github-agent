import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '')))

from hayhooks import BasePipelineWrapper, log
from agent_pipeline import agent_pipe

class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        self.pipeline = agent_pipe()

    def run_api(self, url: str) -> str:
        log.trace(f"Running pipeline with urls: {url}")
        result = self.pipeline.run({"url": url})
        return result["issue_resolver_agent"]["messages"][-1].tool_call_result.result
