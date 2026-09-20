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


class LaunchRequest(BaseModel):
    input_prompt: str


@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest):
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

    # TODO: Run the agent synchronously by calling agent.run() with initial_state and saving the result
    updated_state = agent.run(initial_state)

    # TODO: Store the updated state back into the states dictionary using the same id
    states[initial_state.id] = updated_state

    # TODO: Return the updated state instead of the initial state
    return updated_state