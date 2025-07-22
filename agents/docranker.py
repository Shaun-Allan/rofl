import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool
from llm import create_llm
from config import (
    OPENAI_USERNAME,
    OPENAI_PASSWORD,
    OPENAI_AUTH_URL,
    OPENAI_BASE_URL,
    OPENAI_DEPLOYMENT_MODEL,
    PROMPTS
)
from tools import fetch_confluence_pages
from utilities import pretty_print_messages

# Create the LLM
llm = create_llm(
    OPENAI_USERNAME,
    OPENAI_PASSWORD,
    OPENAI_AUTH_URL,
    OPENAI_BASE_URL,
    OPENAI_DEPLOYMENT_MODEL
)

tools = [
    Tool(
        name="fetch_confluence_pages",
        func=fetch_confluence_pages,
        description="Use this tool to search Confluence pages based on a user query. The query should describe what the user is looking for in documentation, such as 'setup SSH key in GitLab'."
    )
]


docranker_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=PROMPTS["docranker"]["system"],
    name="docranker_agent",
)


# for chunk in docranker_agent.stream(
#         {"messages": "onboarding process for gitlab duo"},
#     ):
#         pretty_print_messages(chunk, last_message=True)

