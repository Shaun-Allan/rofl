
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
from typing import Annotated
from langchain_core.tools import tool
from langgraph.types import Send
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt import create_react_agent


llm = create_llm(OPENAI_USERNAME, OPENAI_PASSWORD, OPENAI_AUTH_URL, OPENAI_BASE_URL, OPENAI_DEPLOYMENT_MODEL)

def create_task_description_handoff_tool(
    *, agent_name: str, description: str | None = None
):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        # this is populated by the supervisor LLM
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        # these parameters are ignored by the LLM
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        # print("🛠️ Handoff tool called with task_description:", task_description)
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            # highlight-next-line
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )

    return handoff_tool


assign_to_pipeline_agent_with_description = create_task_description_handoff_tool(
    agent_name="pipeline_agent",
    description="Delegate this task to the Pipeline Agent, an expert in GitLab CI/CD. It specializes in crafting, debugging, and optimizing `.gitlab-ci.yml` files, job workflows, triggers, and automation strategies across environments."
)

assign_to_gitlab_agent_with_description = create_task_description_handoff_tool(
    agent_name="gitlab_agent",
    description="Assign this task to the GitLab Agent, a specialist in GitLab platform features. It handles repository management, merge requests, access control, integrations, and API usage—excluding pipeline logic."
)

assign_to_jira_agent_with_description = create_task_description_handoff_tool(
    agent_name="jira_agent",
    description="Assign this task to the GitLab Agent, a specialist in GitLab platform features. It handles repository management, merge requests, access control, integrations, and API usage—excluding pipeline logic."
)

assign_to_docranker_agent_with_description = create_task_description_handoff_tool(
    agent_name="docranker_agent",
    description="Assign this task to the GitLab Agent, a specialist in GitLab platform features. It handles repository management, merge requests, access control, integrations, and API usage—excluding pipeline logic."
)

assign_to_usersandgroups_agent_with_description = create_task_description_handoff_tool(
    agent_name="usersandgroups_agent",
    description="Assign this task to the Users and Groups Agent, responsible for retrieving user details via RACF ID, access group metadata, and group associations across Jira, Confluence, and GitLab."
)

assign_to_confluence_agent_with_description = create_task_description_handoff_tool(
    agent_name="confluence_agent",
    description="Assign this task to the Confluence Agent, responsible for managing Confluence spaces, pages, permissions, templates, and integrations with Jira and other tools."
)



supervisor_agent = create_react_agent(
    model=llm,
    tools=[
        assign_to_pipeline_agent_with_description,
        assign_to_gitlab_agent_with_description,
        assign_to_jira_agent_with_description,
        assign_to_docranker_agent_with_description,
        assign_to_usersandgroups_agent_with_description,
        assign_to_confluence_agent_with_description, 
    ],
    prompt=PROMPTS["supervisor"]["system"],
    name="supervisor",
    debug=True
)
