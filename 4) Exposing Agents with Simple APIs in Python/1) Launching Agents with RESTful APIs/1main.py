import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

# Create agent
agent = Agent()

# In-memory storage
states: Dict[str, State] = {}

app = FastAPI()

# TODO: Define a Pydantic model called LaunchRequest with a single field: input_prompt of type str
class LaunchRequest(BaseModel):
    input_prompt: str


# TODO: Add response_model=State to the endpoint decorator
@app.post("/agent/launch", response_model=State)
# TODO: Add a parameter 'payload' of type LaunchRequest to accept the request body
def agent_launch(payload: LaunchRequest):
    # TODO: Create an initial State with:
    #   - id set to a new UUID string (use str(uuid.uuid4()))
    #   - context as a list with one dict: {"role": "user", "content": payload.input_prompt}
    #   - status set to "running"
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

    # TODO: Store the initial state in the 'states' dictionary keyed by its id
    states[initial_state.id] = initial_state

    # TODO: Return the initial state
    return initial_state