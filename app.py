from langgraph.graph import StateGraph, START, MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from utilities import pretty_print_messages
from agents import supervisor_agent, pipeline_agent, gitlab_agent, jira_agent, docranker_agent, usersandgroups_agent, confluence_agent
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "your-secret-key"

# Buffer size for memory
BUFFER_SIZE = 10  # You can adjust this number based on your needs

# Build the LangGraph
supervisor_graph = (
    StateGraph(MessagesState)
    .add_node("supervisor", supervisor_agent, destinations=(
        "pipeline_agent",
        "gitlab_agent",
        "jira_agent",
        "docranker_agent",
        "usersandgroups_agent",
        "confluence_agent" 
    ))
    .add_node("pipeline_agent", pipeline_agent)
    .add_node("gitlab_agent", gitlab_agent)
    .add_node("jira_agent", jira_agent)
    .add_node("docranker_agent", docranker_agent)
    .add_node("usersandgroups_agent", usersandgroups_agent)
    .add_node("confluence_agent", confluence_agent) 
    .add_edge(START, "supervisor")
    .add_edge("pipeline_agent", "supervisor")
    .add_edge("gitlab_agent", "supervisor")
    .add_edge("jira_agent", "supervisor")
    .add_edge("docranker_agent", "supervisor")
    .add_edge("usersandgroups_agent", "supervisor")
    .add_edge("confluence_agent", "supervisor") 
    .compile()
)


# In-memory session store
conversations = {}

def get_trimmed_messages(messages, buffer_size):
    """Preserve system messages and trim user/assistant messages to buffer size."""
    system_msgs = [msg for msg in messages if msg["role"] == "system"]
    convo_msgs = [msg for msg in messages if msg["role"] != "system"]
    return system_msgs + convo_msgs[-buffer_size:]


import time
@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    REQUEST_COUNT.labels(method="POST", endpoint="/chat").inc()

    try:
        user_input = request.form.get("prompt")
        session_id = request.form.get("session_id")
        print(session_id)
        # session_id = "shaun"  # Dev override

        if not user_input:
            return jsonify({"error": "Missing 'prompt' in fo rm data"}), 400

        if not session_id or session_id not in conversations:
            conversations[session_id] = {"messages": []}

        conversations[session_id]["messages"].append({"role": "user", "content": user_input})
        trimmed_messages = get_trimmed_messages(conversations[session_id]["messages"], BUFFER_SIZE)

        response_chunks = []
        for chunk in supervisor_graph.stream(
            {"messages": trimmed_messages},
            subgraphs=True,
        ):
            pretty_print_messages(chunk, last_message=True)
            response_chunks.append(chunk)

        if response_chunks:
            _, last_state = response_chunks[-1]
            last = None
            for node_state in last_state.values():
                if "messages" in node_state and node_state["messages"]:
                    last = node_state["messages"][-1]
                    if isinstance(last, AIMessage):
                        conversations[session_id]["messages"].append({
                            "role": "assistant",
                            "content": last.content
                        })
                    else:
                        conversations[session_id]["messages"].append(last)
                    break
            if not last:
                last = {"content": "No assistant message was returned."}
        else:
            last = {"content": "No response generated."}

        return jsonify({
            "session_id": session_id,
            "response": last.content if hasattr(last, "content") else last
        })

    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint="/chat").observe(duration)



from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


# Metrics
REQUEST_COUNT = Counter("chat_requests_total", "Total number of chat requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("chat_request_latency_seconds", "Latency of chat requests", ["endpoint"])

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0", use_reloader=False)
