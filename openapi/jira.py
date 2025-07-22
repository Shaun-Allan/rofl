import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain_community.agent_toolkits.openapi.toolkit import OpenAPIToolkit
from langchain_community.tools.json.tool import JsonSpec
from langchain.prompts import PromptTemplate
from langchain.agents import Tool
import yaml
import os
import base64
from config import (
    OPENAI_USERNAME,
    OPENAI_PASSWORD,
    OPENAI_AUTH_URL,
    OPENAI_API_URL,
    ATLASSIAN_USERNAME,
    ATLASSIAN_PASSWORD,
    PROMPTS
)
from openapi.llm import create_openapi_llm
from openapi.request_wrapper import UnsafeRequestsWrapper



# Load and clean the OpenAPI spec
with open("openapi/spec/jira.yaml", "r") as f:
    raw_spec = yaml.safe_load(f)
 
# Convert response keys to strings if needed
def convert_response_keys_to_strings(spec_dict):
    if "paths" in spec_dict:
        for path, methods in spec_dict["paths"].items():
            for method, details in methods.items():
                if isinstance(details, dict) and "responses" in details:
                    responses = details["responses"]
                    new_responses = {str(k): v for k, v in responses.items()}
                    details["responses"] = new_responses
    return spec_dict
 
 
cleaned_spec = convert_response_keys_to_strings(raw_spec)
json_spec = JsonSpec(dict_=cleaned_spec)

# Set up headers

headers = {
    "Authorization": f"Basic {base64.b64encode(f'{ATLASSIAN_USERNAME}:{ATLASSIAN_PASSWORD}'.encode()).decode()}",
    "Content-Type": "application/json"
}


requests_wrapper = UnsafeRequestsWrapper(headers=headers, verify=False)

llm = create_openapi_llm(OPENAI_USERNAME, OPENAI_PASSWORD, OPENAI_AUTH_URL, OPENAI_API_URL)
 
toolkit = OpenAPIToolkit.from_llm(
    llm=llm,
    json_spec=json_spec,
    requests_wrapper=requests_wrapper,
    allow_dangerous_requests=True,
    verbose=True,
    agent_executor_kwargs={
        "handle_parsing_errors": True,
        "return_intermediate_steps": True,
        "max_iterations": 2
    },
)


# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=['agent_scratchpad', 'input'],
    input_types={}, 
    partial_variables={},
    template=PROMPTS["gitlab_json_explorer"]["system"]
)


tools = toolkit.get_tools()
def extract_final_answer_from_agent(query: str) -> str:
    result = toolkit.json_agent.invoke({"input": query})
    for step in result.get("intermediate_steps", []):
        if isinstance(step, tuple):
            log = getattr(step[0], "log", "")
            if "Final Answer:" in log:
                return log.split("Final Answer:")[-1].strip()
    return result.get("output", "Could not extract final answer.")


# Wrap it as a LangChain Tool
final_answer_tool = Tool(
    name="json_explorer",
    func=extract_final_answer_from_agent,
    description="""
    Can be used to answer questions about the openapi spec for the API. Always use this tool before trying to make a request.
    Example inputs to this tool: 
        'What are the required query parameters for a GET request to the /bar endpoint?`
        'What are the required parameters in the request body for a POST requests to the /foo endpoint?'
    Always give this tool a specific question.
    """
)

toolkit.json_agent.agent.llm_chain.prompt = prompt_template


# print(extract_final_answer_from_agent("what are the required paramters for adding a issue type?"))


# Add it to the tools list
tools = [t if t.name != "json_explorer" else final_answer_tool for t in tools]