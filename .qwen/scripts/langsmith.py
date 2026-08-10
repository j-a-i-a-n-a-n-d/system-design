import json
import os
import time
from uuid import uuid4
from langsmith import RunTree

# Configure LangSmith Environment Variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key_here"
os.environ["LANGCHAIN_PROJECT"] = "qwen-code-observability"

EVENT_FILE = "/tmp/qwen-events.jsonl"

def process_stream():
    """Tails the Qwen event log and creates nested runs in LangSmith."""
    if not os.path.exists(EVENT_FILE):
        open(EVENT_FILE, 'w').close()

    root_trace = None
    active_tools = {}

    print(f"🚀 Telemetry collector listening on {EVENT_FILE}...")

    with open(EVENT_FILE, "r") as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)
                continue

            try:
                event = json.loads(line.strip())
                event_type = event.get("type")

                # 1. Root Session Tracking
                if event_type == "system" and event.get("subtype") == "session_start":
                    session_id = event["data"].get("session_id", str(uuid4()))
                    cwd = event["data"].get("cwd", "")
                    
                    root_trace = RunTree(
                        name="Qwen Code Session",
                        run_type="chain",
                        inputs={"cwd": cwd},
                        extra={"session_id": session_id},
                        project_name=os.getenv("LANGCHAIN_PROJECT")
                    )
                    root_trace.post()
                    print(f"Started trace for Session: {session_id}")

                # 2. User Input Tracking
                elif event_type == "user":
                    if root_trace:
                        user_run = root_trace.create_child(
                            name="User Input",
                            run_type="prompt",
                            inputs={"content": event.get("message", {})}
                        )
                        user_run.post()
                        user_run.end()

                # 3. LLM Generation & Token Usage Dashboard
                elif event_type == "assistant":
                    if root_trace:
                        msg = event.get("message", {})
                        usage = msg.get("usage", {})
                        
                        # Populate Token Metrics explicitly for LangSmith Dashboard
                        extra_data = {
                            "usage": usage,
                            "prompt_tokens": usage.get("input_tokens", 0),
                            "completion_tokens": usage.get("output_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0)
                        }

                        llm_run = root_trace.create_child(
                            name="Qwen Code LLM Turn",
                            run_type="llm",
                            inputs={},
                            outputs={"message": msg.get("content")},
                            extra=extra_data
                        )
                        llm_run.post()
                        llm_run.end()

                # 4. Tool Execution Tracking (Commands, File Edits, MCP Tools)
                elif event_type == "control_request":
                    request = event.get("request", {})
                    req_id = event.get("request_id")
                    tool_name = request.get("tool_name", "tool_call")
                    
                    if root_trace:
                        tool_run = root_trace.create_child(
                            name=f"Tool: {tool_name}",
                            run_type="tool",
                            inputs=request.get("input", {})
                        )
                        tool_run.post()
                        active_tools[req_id] = tool_run

                elif event_type == "control_response":
                    response = event.get("response", {})
                    req_id = response.get("request_id")
                    
                    if req_id in active_tools:
                        tool_run = active_tools.pop(req_id)
                        allowed = response.get("response", {}).get("allowed", False)
                        tool_run.end(outputs={"permission_allowed": allowed})

                # 5. Session Completion
                elif event_type == "system" and event.get("subtype") == "session_end":
                    if root_trace:
                        root_trace.end()
                        print("Session ended cleanly.")
                        root_trace = None

            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    process_stream()