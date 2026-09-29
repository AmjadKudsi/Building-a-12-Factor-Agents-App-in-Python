import time
import requests

BASE_URL = "http://localhost:8000"

# === Part 1: Launch and pause a running agent ===
print("=== Launching agent ===")
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)
state = response.json()
agent_id = state["id"]
print(f"Launched agent with ID: {agent_id}")
print(f"Initial status: {state['status']}")

# Wait a bit so the agent starts processing
time.sleep(3)

# Call the pause endpoint
print("\n=== Calling /agent/pause ===")
response = requests.post(
    f"{BASE_URL}/agent/pause",
    json={"id": agent_id}
)
print(f"Pause response status code: {response.status_code}")
paused_state = response.json()
if response.status_code == 200:
    print(f"Status: {paused_state['status']} | Steps: {paused_state['steps']}")
else:
    print(f"Unexpected response: {paused_state}")

# Poll until the agent actually shows "paused" in state
print("\n=== Polling for paused status ===")
max_polls = 15
for i in range(max_polls):
    response = requests.get(f"{BASE_URL}/agent/state/{agent_id}")
    current_state = response.json()
    print(f"Poll {i+1}: status={current_state['status']} | steps={current_state['steps']}")

    if current_state["status"] == "paused":
        print("\nAgent is confirmed paused!")
        break

    if current_state["status"] in ["complete", "max_steps_reached", "failed"]:
        print(f"\nAgent finished with status '{current_state['status']}' before pausing.")
        break

    time.sleep(1)
else:
    print("\nTimed out waiting for agent to pause.")

# === Part 2: Try to pause the same agent again (should fail with 400) ===
print("\n=== Attempting to pause the already-paused agent ===")
response = requests.post(
    f"{BASE_URL}/agent/pause",
    json={"id": agent_id}
)
print(f"Status code: {response.status_code}")
print(f"Response body: {response.json()}")

if response.status_code == 400:
    print("Correct! Cannot pause an agent that is not running.")
else:
    print("ERROR: Expected status code 400 for double-pause attempt.")

# === Part 3: Try to pause a non-existent agent (should fail with 404) ===
print("\n=== Attempting to pause a non-existent agent ===")
response = requests.post(
    f"{BASE_URL}/agent/pause",
    json={"id": "does-not-exist-id"}
)
print(f"Status code: {response.status_code}")
print(f"Response body: {response.json()}")

if response.status_code == 404:
    print("Correct! Non-existent agent returns 404.")
else:
    print("ERROR: Expected status code 404 for non-existent agent.")