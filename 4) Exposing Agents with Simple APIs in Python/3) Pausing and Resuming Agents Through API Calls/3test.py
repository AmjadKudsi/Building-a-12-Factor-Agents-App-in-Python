import time
import requests

BASE_URL = "http://localhost:8000"

# === Part 1: Launch, pause, resume, and complete ===
print("=== Launching agent ===")
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
)
state = response.json()
agent_id = state["id"]
print(f"Launched agent with ID: {agent_id}")
print(f"Initial status: {state['status']}")

# Wait for the agent to start processing
time.sleep(3)

# Pause the agent
print("\n=== Pausing agent ===")
response = requests.post(
    f"{BASE_URL}/agent/pause",
    json={"id": agent_id}
)
paused_state = response.json()
print(f"Pause response status code: {response.status_code}")
if response.status_code == 200:
    print(f"Status: {paused_state['status']} | Steps: {paused_state['steps']}")
else:
    print(f"Unexpected response: {paused_state}")

# Wait for the agent to actually stop
time.sleep(2)

# Confirm it is paused
response = requests.get(f"{BASE_URL}/agent/state/{agent_id}")
current = response.json()
print(f"Confirmed status after pause: {current['status']}")

# Resume the agent
print("\n=== Resuming agent ===")
response = requests.post(
    f"{BASE_URL}/agent/resume",
    json={"id": agent_id}
)
print(f"Resume response status code: {response.status_code}")
resumed_state = response.json()
if response.status_code == 200:
    print(f"Resumed agent. Status: {resumed_state['status']}")
else:
    print(f"Unexpected response: {resumed_state}")

# === Part 2: Immediately try to resume again (should get 409 Conflict) ===
print("\n=== Attempting duplicate resume (expect 409) ===")
response = requests.post(
    f"{BASE_URL}/agent/resume",
    json={"id": agent_id}
)
print(f"Status code: {response.status_code}")
print(f"Response body: {response.json()}")
if response.status_code == 409:
    print("Correct! Duplicate resume blocked with 409 Conflict.")
else:
    print("ERROR: Expected status code 409 for duplicate resume attempt.")

# === Part 3: Poll until the agent completes ===
print("\n=== Polling for completion ===")
max_polls = 30
for i in range(max_polls):
    response = requests.get(f"{BASE_URL}/agent/state/{agent_id}")
    current_state = response.json()
    print(f"Poll {i+1}: status={current_state['status']} | steps={current_state['steps']}")

    if current_state["status"] in ["complete", "max_steps_reached", "failed"]:
        print(f"\nFinal status: {current_state['status']}")
        print(f"Final answer: {current_state.get('final_answer')}")
        break

    time.sleep(1)
else:
    print("\nTimed out waiting for agent to complete.")

# === Part 4: Try to resume a non-existent agent (should get 404) ===
print("\n=== Attempting to resume non-existent agent (expect 404) ===")
response = requests.post(
    f"{BASE_URL}/agent/resume",
    json={"id": "does-not-exist-id"}
)
print(f"Status code: {response.status_code}")
print(f"Response body: {response.json()}")
if response.status_code == 404:
    print("Correct! Non-existent agent returns 404.")
else:
    print("ERROR: Expected status code 404 for non-existent agent.")