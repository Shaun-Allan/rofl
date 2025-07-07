import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm import create_llm
from config import *
from langgraph.prebuilt import create_react_agent
from openapi.gitlab import tools
from utilities.print import *
from openapi.gitlab import *

llm = create_llm()

pipeline_agent = create_react_agent(
    model=llm,
    tools=toolkit.json_agent.tools,
    prompt="""'You are an agent designed to interact with JSON.\nYour goal is to return a final answer by interacting with the JSON.\nYou have access to the following tools which help you learn more about the JSON you are interacting with.\nOnly use the below tools. Only use the information returned by the below tools to construct your final answer.\nDo not make up any information that is not contained in the JSON.\nYour input to the tools should be in the form of `data["key"][0]` where `data` is the JSON blob you are interacting with, and the syntax used is Python.  If data['endpoints'] is a list of tuples, iterate through them and match the first element (the method and path) to the user's intention. Only proceed with the one that matches. do not blindly give data["key"][0] \nYou should only use keys that you know for a fact exist. You must validate that a key exists by seeing it previously when calling `json_spec_list_keys`. \nIf you have not seen a key in one of those responses, you cannot use it.\nYou should only add one key at a time to the path. . You cannot add multiple keys at once.\nIf you encounter a "KeyError", go back to the previous key, look at the available keys, and try again.\n\nIf the question does not seem to be related to the JSON, just return "I don\'t know" as the answer.\nAlways begin your interaction with the `json_spec_list_keys` tool with input "data" to see what keys exist in the JSON.\n\nNote that sometimes the value at a given path is large. In this case, you will get an error "Value is a large dictionary, should explore its keys directly".\nIn this case, you should ALWAYS follow up by using the `json_spec_list_keys` tool to see what keys exist at that path.\nDo not simply refer the user to the JSON or a section of the JSON, as this is not a valid answer. Keep digging until you find the answer and explicitly return it.\n\n\njson_spec_list_keys - \n    Can be used to list all keys at a given path. \n    Before calling this you should be SURE that the path to this exists.\n    The input is a text representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"]).\n    \njson_spec_get_value - \n    Can be used to see value in string format at a given path.\n    Before calling this you should be SURE that the path to this exists.\n    The input is a text representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"]).\n  If a value is a large dictionary, do not try to get the full value. Instead, use json_spec_list_keys on that path to explore its keys.""",
    name="json_agent",
)

for chunk in pipeline_agent.stream(
    {"messages": [{"role": "user", "content": "what are the required paramters for triggeriung a manual job"}]}
):
    pretty_print_messages(chunk)


# print(toolkit.json_agent)



