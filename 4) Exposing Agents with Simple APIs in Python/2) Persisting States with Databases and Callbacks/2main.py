import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, pydantic_to_db, StateModel, db_to_pydantic

# Create agent
agent = Agent()

# In-memory storage (still used by background task)
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
    
    # Persist to database
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)
    
    # Store in memory (still needed for background task)
    states[initial_state.id] = initial_state
    
    # Run agent in background (non-blocking)
    background_tasks.add_task(_run_agent_in_background, initial_state.id)
    
    return initial_state

@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    # TODO: Open a database session using get_db_session() as a context manager
    # TODO: Query StateModel filtering by StateModel.id == state_id, using .first()
    # TODO: If no record is found, raise HTTPException(status_code=404, detail="State not found")
    # TODO: Convert the database model to Pydantic using db_to_pydantic() and return it
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == state_id)
            .first()
        )

        if db_state is None:
            raise HTTPException(status_code=404, detail="State not found")

        return db_to_pydantic(db_state)