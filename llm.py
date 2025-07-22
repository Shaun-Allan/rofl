
from langchain_openai.chat_models.base import ChatOpenAI
import requests

import httpx



def get_jwt(username, password, auth_url):
    headers = {
        'Authorization': f'Basic {requests.auth._basic_auth_str(username, password).split(" ")[1]}',
        'Accept': 'text/plain'
    }
    response = requests.post(auth_url, headers=headers)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"JWT auth failed: {response.status_code} - {response.text}")



def create_llm(username, password, auth_url, base_url, deployment_model):
    jwt_token = get_jwt(username, password, auth_url)

    # Custom HTTP clients with SSL disabled (for dev)
    custom_http_client = httpx.Client(verify=False)
    custom_async_client = httpx.AsyncClient(verify=False)
    
    return ChatOpenAI(
        base_url=base_url,
        model=deployment_model,
        openai_api_key="not-needed", #Place holder as we are passsing thte jwt token
        default_headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        default_query={"api-version": "2023-05-15"}, 
        model_kwargs={"tool_choice": "auto"},
        http_client=custom_http_client,
        http_async_client=custom_async_client
    )
    
