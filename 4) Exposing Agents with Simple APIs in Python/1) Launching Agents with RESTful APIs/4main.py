import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
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

def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread (non-blocking)"""
    state = states[state_id]
    state = agent.run(state)
    states[state_id] = state

@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
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

    states[initial_state.id] = initial_state
    background_tasks.add_task(_run_agent_in_background, initial_state.id)

    return initial_state

# TODO: Add a GET endpoint decorator for the path "/agent/state/{state_id}" with response_model=State
@app.get("/agent/state/{state_id}", response_model=State)

# TODO: Define a function called get_state that accepts a state_id parameter of type str
def get_state(state_id: str):
    # TODO: If state_id is not in the states dictionary, raise HTTPException with status_code=404 and detail="State not found"
    if state_id not in states:
        raise HTTPException(status_code=404, detail="State not found")

    # TODO: Otherwise, return the state from the states dictionary for the given state_id
    return states[state_id]