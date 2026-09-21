import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

# Create agent
agent = Agent()

# In-memory storage
states: Dict[str, State] = {}

app = FastAPI()

class LaunchRequest(BaseModel):
    input_prompt: str

# TODO: Create a helper function called _run_agent_in_background that takes a state_id (str),
#       loads the state from the states dictionary, runs agent.run(state),
#       and stores the updated state back into states[state_id]
def _run_agent_in_background(state_id: str):
    state = states[state_id]
    updated_state = agent.run(state)
    states[state_id] = updated_state


@app.post("/agent/launch", response_model=State)
# TODO: Add a background_tasks parameter of type BackgroundTasks to the function signature
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    # Create initial state with unique ID
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )

    # Store in memory
    states[initial_state.id] = initial_state

    # TODO: Replace the two lines below with a single background_tasks.add_task() call
    #       that schedules _run_agent_in_background with initial_state.id
    background_tasks.add_task(
        _run_agent_in_background,
        initial_state.id
    )

    # TODO: Return initial_state instead of updated_state so the endpoint responds immediately
    return initial_state