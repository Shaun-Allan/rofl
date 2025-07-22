from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from langgraph.graph import StateGraph
from your_langchain_definitions import (
    MessagesState, supervisor_agent,
    usersandgroups_agent, confluence_agent,
    gitlab_agent, pipeline_agent
)
from langchain_core.messages import AIMessage
import time
import threading
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# ------------------------------
# Flask Setup
# ------------------------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------
# Metrics
# ------------------------------
REQUEST_COUNT = Counter('http_requests_total', 'HTTP Request Count', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])

# ------------------------------
# LangGraph Setup
# ------------------------------
supervisor_graph = (
    StateGraph(MessagesState)
    .add_node("supervisor", supervisor_agent, destinations=("usersandgroups_agent", "confluence_agent"))
    .add_node("pipeline_agent", pipeline_agent)
    .add_node("gitlab_agent", gitlab_agent)
    .add_edge("confluence_agent", "supervisor")
    .compile()
)

# ------------------------------
# In-Memory Store
# ------------------------------
BUFFER_SIZE = 20
conversations = {}      # session_id -> {"messages": [...], "user": {...}}
user_queue = []         # List of users waiting for human agents

# ------------------------------
# Helpers
# ------------------------------
def get_trimmed_messages(messages, buffer_size):
    system_msgs = [msg for msg in messages if msg["role"] == "system"]
    convo_msgs = [msg for msg in messages if msg["role"] != "system"]
    return system_msgs + convo_msgs[-buffer_size:]

def escalate_to_human(session_id):
    user_data = conversations[session_id].get("user", {})
    user_obj = {
        "id": session_id,
        "name": user_data.get("name", "Unnamed"),
        "email": user_data.get("email", "unknown@user.com"),
        "timestamp": datetime.utcnow().isoformat()
    }
    if not any(u["id"] == session_id for u in user_queue):
        user_queue.append(user_obj)
        socketio.emit("user_queue_update", {"queue": user_queue}, broadcast=True)
        print(f"[Escalation] User {session_id} added to human agent queue.")

# ------------------------------
# Chat REST endpoint
# ------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    REQUEST_COUNT.labels(method="POST", endpoint="/chat").inc()

    user_input = request.form.get("prompt")
    session_id = request.form.get("session_id")
    name = request.form.get("name", "User")
    email = request.form.get("email", "user@unknown.com")

    if not user_input:
        return jsonify({"error": "Missing prompt"}), 400

    if session_id not in conversations:
        conversations[session_id] = {
            "messages": [],
            "user": {"name": name, "email": email}
        }

    conversations[session_id]["messages"].append({"role": "user", "content": user_input})

    trimmed_messages = get_trimmed_messages(conversations[session_id]["messages"], BUFFER_SIZE)
    response_chunks = []
    success_flag = {"done": False, "response": None}

    def run_langgraph():
        try:
            for chunk in supervisor_graph.stream(
                {"messages": trimmed_messages},
                subgraphs=True,
            ):
                response_chunks.append(chunk)
            success_flag["done"] = True
        except Exception as e:
            print(f"[LangGraph Error] {e}")

    thread = threading.Thread(target=run_langgraph)
    thread.start()
    thread.join(timeout=120)

    if not success_flag["done"]:
        escalate_to_human(session_id)
        return jsonify({"response": "The system is taking too long. You'll be connected to a human agent."})

    # Process last message
    if response_chunks:
        _, last_state = response_chunks[-1]
        last = None
        for node_state in last_state.values():
            if "messages" in node_state and node_state["messages"]:
                last = node_state["messages"][-1]
                if isinstance(last, AIMessage):
                    conversations[session_id]["messages"].append({"role": "assistant", "content": last.content})
                    success_flag["response"] = last.content
                else:
                    conversations[session_id]["messages"].append(last)
                    success_flag["response"] = last.get("content", "")
                break

    if success_flag["response"] is None:
        escalate_to_human(session_id)
        return jsonify({"response": "We couldn't generate a valid response. Redirecting you to a human agent..."})

    duration = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint="/chat").observe(duration)

    return jsonify({
        "session_id": session_id,
        "response": success_flag["response"]
    })

# ------------------------------
# WebSocket Events
# ------------------------------
@socketio.on('connect')
def handle_connect():
    print("[Client Connected]")

@socketio.on('join_agent_dashboard')
def join_dashboard():
    emit("user_queue_update", {"queue": user_queue})

@socketio.on('agent_connect_user')
def connect_agent_to_user(data):
    session_id = data.get("session_id")
    agent_name = data.get("agent_name", "Agent")
    print(f"[Agent Connect] {agent_name} connecting to user {session_id}")

    # Remove from queue
    global user_queue
    user_queue = [u for u in user_queue if u["id"] != session_id]
    socketio.emit("user_queue_update", {"queue": user_queue})

    # Notify the chatbot frontend
    socketio.emit("human_connected", {"session_id": session_id, "agent_name": agent_name}, room=session_id)

@socketio.on("user_chat")
def forward_user_message(data):
    session_id = data["session_id"]
    message = data["message"]
    join_room(session_id)
    emit("chat_message", {"sender": "user", "message": message}, to=session_id)

@socketio.on("agent_chat")
def forward_agent_message(data):
    session_id = data["session_id"]
    message = data["message"]
    emit("chat_message", {"sender": "agent", "message": message}, to=session_id)

@socketio.on("leave_chat")
def leave_chat(data):
    session_id = data.get("session_id")
    leave_room(session_id)
    print(f"[Leave Chat] Session {session_id} left.")

# ------------------------------
# Prometheus Metrics Endpoint
# ------------------------------
@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# ------------------------------
# Run App
# ------------------------------
if __name__ == '__main__':
    import eventlet
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
