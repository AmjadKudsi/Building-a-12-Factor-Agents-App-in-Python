import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Create agent
agent = Agent()

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the database"""
    # TODO: Open a DB session and query StateModel by state_id using .first()
    # TODO: If no row is found, return early
    # TODO: Convert the database row to a Pydantic State using db_to_pydantic()
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == state_id)
            .first()
        )

        if not db_state:
            return

        working_state = db_to_pydantic(db_state)

    # TODO: Run the agent with agent.run() on the working state (no callbacks needed)
    final_state = agent.run(working_state)

    # TODO: Open a new DB session and query the same row again by state_id
    # TODO: If found, update its fields (steps, status, context, pending_tool_calls, error, final_answer) from the final state
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == state_id)
            .first()
        )

        if db_state:
            db_state.steps = final_state.steps
            db_state.status = final_state.status
            db_state.context = final_state.context
            db_state.pending_tool_calls = final_state.pending_tool_calls
            db_state.error = final_state.error
            db_state.final_answer = final_state.final_answer


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

    # Run agent in background (non-blocking)
    background_tasks.add_task(_run_agent_in_background, initial_state.id)

    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == state_id)
            .first()
        )

        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")

        return db_to_pydantic(db_state)