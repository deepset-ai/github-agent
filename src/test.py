from agent_pipeline import agent_pipe

issue_url = "https://github.com/deepset-ai/haystack-core-integrations/issues/1268"
result = agent_pipe().run({"url": issue_url})
# print(result["issue_resolver_agent"]["messages"][-1])
print(result["issue_resolver_agent"]["messages"][-1].tool_call_result.result)