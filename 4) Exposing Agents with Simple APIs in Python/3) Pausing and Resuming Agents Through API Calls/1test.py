import sys
import time
import requests

# Add src to path so we can import database utilities
sys.path.insert(0, "src")

BASE_URL = "http://localhost:8000"

# Step 1: Launch a new agent
print("=== Launching agent ===")
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)
state = response.json()
agent_id = state["id"]
print(f"Launched agent with ID: {agent_id}")
print(f"Initial status: {state['status']}")

# Step 2: Wait briefly for agent to start processing
time.sleep(3)

# Step 3: Directly set DB status to "paused" (simulating an external pause signal)
print("\n=== Setting DB status to 'paused' directly ===")
from server.database import get_db_session, StateModel

with get_db_session() as session:
    db_state = session.query(StateModel).filter(StateModel.id == agent_id).first()
    if db_state:
        db_state.status = "paused"
        print("Database status set to 'paused'")
    else:
        print("ERROR: State not found in database!")
        sys.exit(1)

# Step 4: Poll until agent shows "paused" status
print("\n=== Polling for paused status ===")
max_polls = 15
for i in range(max_polls):
    response = requests.get(f"{BASE_URL}/agent/state/{agent_id}")
    current_state = response.json()
    print(f"Poll {i+1}: status={current_state['status']} | steps={current_state['steps']}")

    if current_state["status"] == "paused":
        print("\n=== Agent paused successfully! ===")
        print(f"Final status: {current_state['status']}")
        print(f"Steps completed: {current_state['steps']}")

        # Verify the status stays paused (not overwritten back to "running")
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/agent/state/{agent_id}")
        recheck = response.json()
        if recheck["status"] == "paused":
            print("Confirmed: status is still 'paused' (callback did not overwrite it)")
        else:
            print(f"ERROR: Status changed to '{recheck['status']}' - callback may be overwriting 'paused'!")
        break

    if current_state["status"] in ["complete", "max_steps_reached", "failed"]:
        print(f"\nERROR: Agent finished with status '{current_state['status']}' before detecting pause!")
        print("The progress callback is not checking for the pause signal.")
        break

    time.sleep(1)
else:
    print("\nERROR: Timed out waiting for agent to pause.")