from dotenv import load_dotenv
import os
import yaml 

load_dotenv()

OPENAI_USERNAME = os.getenv("OPENAI_USERNAME")
OPENAI_PASSWORD = os.getenv("OPENAI_PASSWORD")
OPENAI_AUTH_URL = os.getenv("OPENAI_AUTH_URL")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_DEPLOYMENT_MODEL = os.getenv("OPENAI_DEPLOYMENT_MODEL")

GITLAB_PERSONAL_ACCESS_TOKEN = os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
GITLAB_BASE_URL = os.getenv("GITLAB_BASE_URL")
GITLAB_DOC_PATH = os.getenv("GITLAB_DOC_PATH")

LDAP_SERVER = os.getenv("LDAP_SERVER")
BIND_DN = os.getenv("BIND_DN")
BIND_PASSWORD = os.getenv("BIND_PASSWORD")
BASE_DN = os.getenv("BASE_DN")

ATLASSIAN_BASE_URL = os.getenv("ATLASSIAN_BASE_URL")
ATLASSIAN_API_BASE_URL = f'{ATLASSIAN_BASE_URL}/rest/api'
ATLASSIAN_USERNAME = os.getenv("ATLASSIAN_USERNAME")
ATLASSIAN_PASSWORD = os.getenv("ATLASSIAN_PASSWORD")


with open("prompts.yaml", "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

