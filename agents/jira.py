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
from openapi import JIRA_TOOLS


llm = create_llm(OPENAI_USERNAME, OPENAI_PASSWORD, OPENAI_AUTH_URL, OPENAI_BASE_URL, OPENAI_DEPLOYMENT_MODEL)

jira_agent = create_react_agent(
    model=llm,
    tools=JIRA_TOOLS,
    prompt=PROMPTS["jira"]["system"],
    name="jira_agent",
)