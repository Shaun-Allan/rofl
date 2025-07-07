# 🧠 Developer Support Assistant (Backend)

> ## NOTE: Features and architecture not updated. You will be seeing an earlier version while the code presented reflects the up-to-date version

This project is a smart, autonomous assistant built using **LangChain**, **Flask**, and a **custom JWT-authenticated OpenAI LLM**. It acts as a first-line service desk agent for developers working across platforms like GitLab, Jira, Confluence, Artifactory, and internal access management systems.



## 🚀 Features

- 🔐 **JWT-authenticated LLM**: Secure integration with OpenAI using JWT tokens.
- 🧠 **LangChain Agent**: Uses a custom prompt template and memory to maintain conversation context.
- 🛠️ **Tool Integration**: Supports tools like LDAP group info and user info retrieval.
- 🗣️ **Natural Language Understanding**: Interprets developer queries and maps them to actionable tasks.
- 🧩 **Context Normalization**: Treats equivalent terms (e.g., RACF ID, sAMAccountName) uniformly.
- 🔄 **Conversation Memory**: Maintains chat history using `ConversationBufferMemory`.
- 🌐 **REST API**: Exposes endpoints for chat interaction and memory reset.
- 🔍 **Multi-Step Reasoning**: Enables the agent to break down complex queries into smaller, logical steps.
- ✍️ **Spelling & Typo Handling**: Detects and corrects common spelling mistakes in user input.




## 🏗️ Project Structure

```
.
├── app.py                  # Main Flask app with endpoints
├── chat_model.py           # Custom LLM class with JWT support
├── tools.py                # Tool functions and registerations
├── .env                    # Environment variables (not committed)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```



## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://natwest.gitlab-dedicated.com/ShaunAllan.H/service-desk-assistant.git
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

### 4. Configure Environment Variables

Create a `.env` file with the following keys:

```env
OPENAI_USERNAME=your_username
OPENAI_PASSWORD=your_password
OPENAI_AUTH_URL=https://auth.example.com/token
OPENAI_API_URL=https://api.openai.com/v1/chat/completions
TOOL_SERVER_URL=https://internal-tools.example.com
```

### 5. Run the App

```bash
python app.py
```

The app will be available at `http://localhost:8000`.



## 🧠 LangChain Agent Design

### Prompt Template

The assistant is guided by a detailed prompt that:

- Defines its role and capabilities.
- Normalizes terminology across platforms.
- Specifies tool usage and response formatting.
- Encourages intelligent escalation when automation is insufficient.

### Memory

Uses `ConversationBufferMemory` to retain chat history and personalize responses.



## 🔧 Available Tools

The tools are defined and hosted in a different server.

> `https://natwest.gitlab-dedicated.com/ShaunAllan.H/service-tools`



## 📡 API Endpoints

### `POST /chat`

**Request:**
```form
prompt=I want to add an issute type to my JIRA project?
```

**Response:**
```json
{ "response": "Please provide the issue types and..." }
```



### `POST /reset`

Clears the conversation memory.

**Response:**
```json
{ "message": "Conversation history reset." }
```



## 📌 Future Enhancements (TODO)

- [ ] Integrate MCP to interact with interfaces.
- [ ] Check MCPs for JFrog (Artifactory)
- [ ] Implement logging and monitoring.
- [ ] Add a verification layer where a human agent would verify the reponse of the AI agent.
- [ ] Implement WebSockets for chatting with a human agent.