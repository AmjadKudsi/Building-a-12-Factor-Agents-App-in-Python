import time
import json
import requests

BASE_URL = "http://localhost:8000"

# Launch a new agent that will likely ask for one missing value (radius/diameter)
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Can you figure out the area of a circle for me? Use pi = 3.14."}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Poll until it's waiting for human input
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(f"Status: {current_state['status']}, Steps: {current_state['steps']}")

    if current_state["status"] == "waiting_human_input":
        question = None
        for item in reversed(current_state.get("context", [])):
            if (
                isinstance(item, dict)
                and item.get("type") == "function_call"
                and item.get("name") == "ask_human"
            ):
                args = item.get("arguments")
                try:
                    args_dict = json.loads(args) if isinstance(args, str) else (args or {})
                except json.JSONDecodeError:
                    args_dict = {}
                question = args_dict.get("question")
                break

        print(f"Question: {question}")
        break

    if current_state["status"] in ["complete", "max_steps_reached", "failed"]:
        print(f"Completed: {current_state.get('final_answer')}")
        break

    time.sleep(1)