import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Create agent
agent = Agent(max_steps=10)

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


class PauseRequest(BaseModel):
    id: str


# TODO: Define a ResumeRequest model with a single field: id (str)
class ResumeRequest(BaseModel):
    id: str


def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                # Check if status was changed to "paused" externally
                if db_state.status == "paused":
                    # Update local state to paused so agent loop will exit
                    state.status = "paused"
                    # Don't overwrite the paused status - just save other fields
                    db_state.steps = state.steps
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                else:
                    # Normal save - update all fields including status
                    db_state.steps = state.steps
                    db_state.status = state.status
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
    return save_progress


# TODO: Update the function signature to accept an optional second parameter:
#   working_state of type Optional[State], defaulting to None
def _run_agent_in_background(
    state_id: str,
    working_state: Optional[State] = None
):
    """Run the agent in a background thread and update the database"""

    # TODO: Handle two modes based on whether working_state was provided:
    #   1. If working_state is None (fresh start):
    #      - Load the state from the database using state_id
    #      - If not found, return early
    #      - Set db_state.status to "running"
    #      - Convert to Pydantic and assign to working_state
    #   2. If working_state is provided (resume):
    #      - Open a DB session, find the state by state_id
    #      - Set db_state.status to "running"
    #      - Use the provided working_state as-is
    if working_state is None:
        # Fresh start
        with get_db_session() as session:
            db_state = (
                session.query(StateModel)
                .filter(StateModel.id == state_id)
                .first()
            )

            if not db_state:
                return

            db_state.status = "running"
            working_state = db_to_pydantic(db_state)

    else:
        # Resume
        with get_db_session() as session:
            db_state = (
                session.query(StateModel)
                .filter(StateModel.id == state_id)
                .first()
            )

            if not db_state:
                return

            db_state.status = "running"

    # Run agent with progress callback
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(
        working_state,
        progress_callback=save_progress
    )

    # Final update
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

    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)

    background_tasks.add_task(
        _run_agent_in_background,
        initial_state.id
    )

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
            raise HTTPException(
                status_code=404,
                detail="State not found"
            )

        return db_to_pydantic(db_state)


@app.post("/agent/pause", response_model=State)
def agent_pause(payload: PauseRequest):
    """Pause a running agent workflow"""
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == payload.id)
            .first()
        )

        if not db_state:
            raise HTTPException(
                status_code=404,
                detail="State not found"
            )

        # Only allow pausing if agent is currently running
        if db_state.status != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause agent. Current status: {db_state.status}"
            )

        # Set status to paused (progress callback will detect this and stop the loop)
        db_state.status = "paused"

        return db_to_pydantic(db_state)


# TODO: Create a POST endpoint at "/agent/resume" that returns a State (response_model=State).
# The handler should accept a ResumeRequest payload and a BackgroundTasks parameter, then:
#   1. Open a database session and query for the state matching payload.id
#   2. If no state is found, raise an HTTPException with status_code=404 and detail="State not found"
#   3. If db_state.status is "running", raise an HTTPException with status_code=409
#      and detail="Agent is already running"
#   4. Set db_state.status to "running"
#   5. Convert the db_state to a Pydantic State (working_state) using db_to_pydantic
#   6. Schedule the background task: background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
#   7. Return working_state
@app.post("/agent/resume", response_model=State)
def agent_resume(
    payload: ResumeRequest,
    background_tasks: BackgroundTasks
):
    """Resume an existing agent workflow"""
    with get_db_session() as session:
        db_state = (
            session.query(StateModel)
            .filter(StateModel.id == payload.id)
            .first()
        )

        if not db_state:
            raise HTTPException(
                status_code=404,
                detail="State not found"
            )

        if db_state.status == "running":
            raise HTTPException(
                status_code=409,
                detail="Agent is already running"
            )

        db_state.status = "running"

        working_state = db_to_pydantic(db_state)

    background_tasks.add_task(
        _run_agent_in_background,
        payload.id,
        working_state
    )

    return working_state