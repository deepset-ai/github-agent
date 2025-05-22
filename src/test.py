from agent_pipeline import agent_pipe
import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.DEBUG)

issue_url = "https://github.com/bilgeyucel/haystack-aidev25/issues/6"
result = agent_pipe().run({"url": issue_url})

print(result["issue_resolver_agent"]["messages"][-1].tool_call_result.result)
