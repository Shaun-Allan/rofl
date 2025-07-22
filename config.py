from dotenv import load_dotenv
import os
import yaml 
import urllib

load_dotenv()

OPENAI_USERNAME = os.getenv("OPENAI_USERNAME")
OPENAI_PASSWORD = os.getenv("OPENAI_PASSWORD")
OPENAI_AUTH_URL = os.getenv("OPENAI_AUTH_URL")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_DEPLOYMENT_MODEL = os.getenv("OPENAI_DEPLOYMENT_MODEL")

GITLAB_PERSONAL_ACCESS_TOKEN = os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
GITLAB_BASE_URL = os.getenv("GITLAB_BASE_URL")

LDAP_SERVER = os.getenv("LDAP_SERVER")
BIND_DN = os.getenv("BIND_DN")
BIND_PASSWORD = os.getenv("BIND_PASSWORD")
BASE_DN = os.getenv("BASE_DN")

ATLASSIAN_BASE_URL = os.getenv("ATLASSIAN_BASE_URL")
ATLASSIAN_BASE_URL_WIKI = f'{ATLASSIAN_BASE_URL}/wiki'
ATLASSIAN_API_BASE_URL = f'{ATLASSIAN_BASE_URL_WIKI}/rest/api'
ATLASSIAN_USERNAME = os.getenv("ATLASSIAN_USERNAME")
ATLASSIAN_PASSWORD = os.getenv("ATLASSIAN_PASSWORD")
JIRA_ENDPOINT = os.getenv("JIRA_ENDPOINT")
CONFLUENCE_ENDPOINT = os.getenv("CONFLUENCE_ENDPOINT")

with open("prompts.yaml", "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)
    
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = urllib.parse.quote(os.getenv("PROXY_PASSWORD"), safe='')
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")

PROXIES = {
    'http' : 'http://{}:{}@{}:{}'.format(PROXY_USERNAME,PROXY_PASSWORD,PROXY_HOST,PROXY_PORT),
    'https' : 'http://{}:{}@{}:{}'.format(PROXY_USERNAME,PROXY_PASSWORD,PROXY_HOST,PROXY_PORT),
}



DEV_GITLAB_ID = os.getenv("DEV_GITLAB_ID")
DEV_GITLAB_ROLE = os.getenv("DEV_GITLAB_ROLE")