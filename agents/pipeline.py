import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm import create_llm
from config import (
    OPENAI_USERNAME,
    OPENAI_PASSWORD,
    OPENAI_AUTH_URL,
    OPENAI_BASE_URL,
    OPENAI_DEPLOYMENT_MODEL,
    PROMPTS
) 
from langgraph.prebuilt import create_react_agent
from openapi import GITLAB_TOOLS
from tools import GITLAB_TARGETS, fetch_gitlab_documents



from langchain_core.tools import Tool

def fetch_gitlab_documents_tool(input: dict) -> str:
    project_path = input.get("project_path")
    ref = input.get("ref")
    if not project_path or not ref:
        return "❌ Missing 'project_path' or 'ref' in input."
    return fetch_gitlab_documents(project_path, ref)

GITLAB_TOOLS.append(
    Tool(
        name="fetch_gitlab_documents",
        description="Fetches and returns the content of all Markdown (.md) files from a GitLab repository at a specific ref.",
        func=fetch_gitlab_documents_tool
    )
)



llm = create_llm(OPENAI_USERNAME, OPENAI_PASSWORD, OPENAI_AUTH_URL, OPENAI_BASE_URL, OPENAI_DEPLOYMENT_MODEL)

pipeline_agent = create_react_agent(
    model=llm,
    tools=GITLAB_TOOLS,
    prompt=PROMPTS["pipeline"]["system"],
    name="pipeline_agent",
)