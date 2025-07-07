from langgraph.graph import StateGraph, START, MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from utilities import pretty_print_messages
from agents import supervisor_agent, pipeline_agent, gitlab_agent
from flask import Flask, request, jsonify
from flask_cors import CORS
# import uuid


app = Flask(__name__)
CORS(app)
app.secret_key = "your-secret-key"


# Build the LangGraph
supervisor_graph = (
    StateGraph(MessagesState)
    .add_node("supervisor", supervisor_agent, destinations=("pipeline_agent",))
    .add_node("pipeline_agent", pipeline_agent)
    .add_node("gitlab_agent", gitlab_agent)
    .add_edge(START, "supervisor")
    .add_edge("pipeline_agent", "supervisor")
    .add_edge("gitlab_agent", "supervisor")
    .compile()
)


# In-memory session store --> dev specific.. when prod can leverage efficient scalable memory
conversations = {}

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("prompt")
    session_id = request.form.get("session_id")
    session_id = "shaun"  # ---------------------------------------------> dev purposes

    if not user_input:
        return jsonify({"error": "Missing 'message' in form data"}), 400

    if not session_id or session_id not in conversations:
        # session_id = str(uuid.uuid4())
        conversations[session_id] = {"messages": []}


    # Add user message to session
    conversations[session_id]["messages"].append({"role": "user", "content": user_input})

    # Run LangGraph stream
    response_chunks = []
    for chunk in supervisor_graph.stream(
        {"messages": conversations[session_id]["messages"]},
        subgraphs=True,
    ):
        pretty_print_messages(chunk, last_message=True)
        response_chunks.append(chunk)
    
    # Extract last assistant message
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


if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=False)
