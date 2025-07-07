import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm import get_jwt

from langchain.llms.base import LLM
from pydantic import Field
import requests


class CustomOpenAI(LLM):
    api_url: str = Field(...)
    jwt_token: str = Field(...)

    def _call(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    @property
    def _llm_type(self) -> str:
        return "custom-openai"
    
    
def create_openapi_llm(username, password, auth_url, api_url):
    return CustomOpenAI(
        api_url=api_url,
        jwt_token=get_jwt(username, password, auth_url)
    )