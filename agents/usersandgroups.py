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
from langchain_core.tools import Tool
from tools import get_user_info, get_access_group_info, get_confluence_space_role_groups, get_jira_project_role_groups, get_gitlab_role_groups, get_gitlab_group_id_based_on_bl

# Initialize LLM
llm = create_llm(
    OPENAI_USERNAME,
    OPENAI_PASSWORD,
    OPENAI_AUTH_URL,
    OPENAI_BASE_URL,
    OPENAI_DEPLOYMENT_MODEL
)
from pydantic import BaseModel

# Argument schemas
class GetUserInfoArgs(BaseModel):
    racf_id: str

class GetAccessGroupInfoArgs(BaseModel):
    group_name: str

class GetConfluenceSpaceRoleGroupsArgs(BaseModel):
    space_key: str

class GetJiraProjectRoleGroupsArgs(BaseModel):
    project_key: str

class GetGitlabGroupIdArgs(BaseModel):
    group_bl: str

class GetGitlabRoleGroupsArgs(BaseModel):
    group_id: str


# Tool definitions
get_user_info_tool = Tool.from_function(
    name="get_user_info",
    description="Fetch LDAP user information based on RACF ID or email.",
    func=get_user_info,
    args_schema=GetUserInfoArgs
)

get_access_group_info_tool = Tool.from_function(
    name="get_access_group_info",
    description="Retrieve access group details by group name.",
    func=get_access_group_info,
    args_schema=GetAccessGroupInfoArgs
)

get_confluence_space_role_groups_tool = Tool.from_function(
    name="get_confluence_space_role_groups",
    description="Retrieve role groups for one or more Confluence spaces based on space keys.",
    func=get_confluence_space_role_groups,
    args_schema=GetConfluenceSpaceRoleGroupsArgs
)

get_jira_project_role_groups_tool = Tool.from_function(
    name="get_jira_project_role_groups",
    description="Retrieve role groups for one or more Jira projects based on project keys.",
    func=get_jira_project_role_groups,
    args_schema=GetJiraProjectRoleGroupsArgs
)

get_gitlab_group_id_tool = Tool.from_function(
    name="get_gitlab_group_id_based_on_bl",
    description="Fetch the GitLab group ID based on the business line (group full path).",
    func=get_gitlab_group_id_based_on_bl,
    args_schema=GetGitlabGroupIdArgs
)

get_gitlab_role_groups_tool = Tool.from_function(
    name="get_gitlab_role_groups",
    description="Fetch the SAML role groups for a GitLab group ID.",
    func=get_gitlab_role_groups,
    args_schema=GetGitlabRoleGroupsArgs
)


# Create usersandgroups_agent with all tools
usersandgroups_agent = create_react_agent(
    model=llm,
    tools=[
        get_user_info_tool,
        get_access_group_info_tool,
        get_confluence_space_role_groups_tool,
        get_jira_project_role_groups_tool,
        get_gitlab_group_id_tool,
        get_gitlab_role_groups_tool
    ],
    prompt=PROMPTS["usersandgroups"]["system"],
    name="usersandgroups_agent",
)


# from utilities import pretty_print_messages
# for chunk in usersandgroups_agent.stream(
#         {"messages": "what are the role groups under the comnfluence space ENP?"},
#     ):
#         pretty_print_messages(chunk, last_message=True)

