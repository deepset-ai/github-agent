import os
from getpass import getpass
from typing import List

# Standard Haystack imports
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage, Document
from haystack_integrations.components.generators.anthropic.chat.chat_generator import AnthropicChatGenerator

# Experimental imports needed for our Agent
from haystack_experimental.components.agents import Agent
from haystack_experimental.tools.component_tool import ComponentTool
from haystack_experimental.tools.from_function import tool
# Import from local modules with correct paths
from agent_prompts.system_prompt import agent_system_prompt
from agent_components.repo_viewer import GithubRepositoryViewer
from agent_components.issue_viewer import GithubIssueViewer
from agent_components.issue_commenter import GithubIssueCommenter

# import logging
# from haystack import tracing
# from haystack.tracing.logging_tracer import LoggingTracer

# logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
# logging.getLogger("haystack").setLevel(logging.DEBUG)

# tracing.tracer.is_content_tracing_enabled = True # to enable tracing/logging content (inputs/outputs)
# tracing.enable_tracing(LoggingTracer(tags_color_strings={"haystack.component.input": "\x1b[35m", "haystack.component.name": "\x1b[1;34m"}))

def doc_to_string(documents) -> str:
    """
    Handles the tool output before conversion to ChatMessage.
    """
    result_str = ""
    for document in documents:
        if document.meta["type"] in ["file", "dir", "error"]:
            result_str += document.content + "\n"
        else:
            result_str += f"File Content for {document.meta['path']}\n\n"
            result_str += document.content

    if len(result_str) > 150_000:
        result_str = result_str[:150_000] + "...(large file can't be fully displayed)"

    return result_str

github_repository_viewer_tool = ComponentTool(
    name="github_repository_viewer",
    component=GithubRepositoryViewer(),
    outputs={
        "message": {"source": "documents", "handler": doc_to_string},
        "documents": {"source": "documents"},
    }
)

github_repository_commenter_tool = ComponentTool(
    name="write_github_comment",
    component=GithubIssueCommenter()
)

@tool
def write_github_comment(comment: str) -> str:
    """
    Use this to create a comment on Github once you finished your exploration.
    """
    # WRITE COMMENT ON GITHUB
    return comment

def agent_pipe():
    github_issue_viewer = GithubIssueViewer()
    issue_template = """
    Issue from: {{ url }}
    {% for document in documents %}
        {% if loop.index == 1 %}
        **Title: {{ document.meta.title }}**
        {% endif %}
        <issue-comment>
        {{document.content}}
        </issue-comment>
    {% endfor %}
    """
    issue_builder = ChatPromptBuilder(template=[ChatMessage.from_user(issue_template)])
    
    ## Agent
    chat_generator = AnthropicChatGenerator(model="claude-3-7-sonnet-20250219", generation_kwargs={"max_tokens": 8000})

    issue_resolver_agent = Agent(
        chat_generator=chat_generator,
        system_prompt=agent_system_prompt,
        tools=[github_repository_viewer_tool, github_repository_commenter_tool],
        exit_condition="write_github_comment",
        state_schema={"documents": {"type": List[Document]}},
    )
    issue_resolver = Pipeline()
    issue_resolver.add_component("issue_viewer", github_issue_viewer)
    issue_resolver.add_component("issue_builder", issue_builder)
    issue_resolver.add_component("issue_resolver_agent", issue_resolver_agent)

    issue_resolver.connect("issue_viewer.documents", "issue_builder.documents")
    issue_resolver.connect("issue_builder.prompt", "issue_resolver_agent.messages")
    return issue_resolver