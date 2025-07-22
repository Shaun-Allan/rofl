# SRE Assistant (Backend)

This project is a smart, autonomous **multi-agent** assistant built using **LangGraph**, **Flask**, and **OpenAI GPT-4.1**. It acts as a first-line service desk agent for developers working across platforms like GitLab, Jira, Confluence, Artifactory, and internal access management systems.

---

## 🚀 Features

- 🔐 **JWT-authenticated LLM**: Secure integration with OpenAI using JWT tokens.
- 🧠 **Multi-Agent LangGraph System**: Each agent specializes in a domain (e.g., Jira, LDAP, Confluence), enabling parallel and collaborative task resolution.
- 🛠️ **Tool Integration**: Supports tools like LDAP group info and user info retrieval.
- 🗣️ **Natural Language Understanding**: Interprets developer queries and maps them to actionable tasks.
- 🧩 **Context Normalization**: Treats equivalent terms (e.g., RACF ID, sAMAccountName) uniformly.
- 🔄 **Conversation Memory**: Maintains chat history using `ConversationBufferMemory`.
- 🌐 **REST API**: Exposes endpoints for chat interaction and memory reset.
- 🔍 **Multi-Step Reasoning**: Enables agents to break down complex queries into smaller, logical steps.
- ✍️ **Spelling & Typo Handling**: Detects and corrects common spelling mistakes in user input.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone git@natwest.gitlab-dedicated.com:ShaunAllan.H/sre-assistant-backend.git
cd service-desk-assistant
```

### 2. Setup Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following structure:

<details>
<summary><strong>Click to expand</strong></summary>

```env
# OpenAI Configuration
OPENAI_USERNAME="your_openai_username"
OPENAI_PASSWORD="your_openai_password"
OPENAI_AUTH_URL="your_openai_auth_url"
OPENAI_API_URL="your_openai_api_url"
OPENAI_BASE_URL="your_openai_base_url"
OPENAI_DEPLOYMENT_MODEL="your_openai_deployment_model"

# GitLab Configuration
GITLAB_PERSONAL_ACCESS_TOKEN="your_gitlab_token"
GITLAB_BASE_URL="your_gitlab_base_url"

# LDAP Configuration
LDAP_SERVER="your_ldap_server"
BIND_DN="your_bind_dn"
BIND_PASSWORD="your_bind_password"
BASE_DN="your_base_dn"

# Atlassian (Jira & Confluence)
ATLASSIAN_BASE_URL="your_atlassian_base_url"
ATLASSIAN_USERNAME="your_atlassian_username"
ATLASSIAN_PASSWORD="your_atlassian_password"
JIRA_ENDPOINT="your_jira_endpoint"
CONFLUENCE_ENDPOINT="your_confluence_endpoint"

# Proxy Configuration
PROXY_USER_EMAIL="your_proxy_email"
PROXY_USERNAME="your_proxy_username"
PROXY_PASSWORD="your_proxy_password"
PROXY_HOST="your_proxy_host"
PROXY_PORT=your_proxy_port

# Developer GitLab Access
DEV_GITLAB_ID="your_dev_gitlab_id"
DEV_GITLAB_ROLE="your_dev_gitlab_role"
```

</details>

---

### 5. Run the App

```bash
python app.py
```

The app will be available at `http://localhost:8000`

---

## 🧠 LangGraph Multi-Agent Design

### Architecture

The assistant now uses a **multi-agent architecture** where each agent is responsible for a specific domain (e.g., Jira, LDAP, Confluence). Agents collaborate using LangGraph to resolve complex queries more efficiently.

### Prompt Template

Each agent is guided by a domain-specific prompt that:

- Defines its role and capabilities.
- Normalizes terminology across platforms.
- Specifies tool usage and response formatting.
- Encourages intelligent escalation when automation is insufficient.


---

## 📡 API Endpoints

### `POST /chat`

**Request:**
```form
prompt=I want to change board administrators to my JIRA project?
```

**Response:**
```json
{ "response": "Please provide the board ID and..." }
```
---

## 📌 Future Enhancements (TODO)

- [ ] Add Artifactory agent
- [ ] Add a verification layer where a human agent would verify the response of the AI agent
- [ ] Implement WebSockets for chatting with a human agent
- [ ] Add agent coordination visualization for debugging and monitoring