import uuid
from core.models.state import State

# TODO: Create a State instance with:
# - id set to a generated UUID string (use str(uuid.uuid4()))
# - context set to a list with one user message dict (role="user", content with a simple request)
# - Leave steps and status unset to exercise their defaults
state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "What is 2 + 2?"
        }
    ]
)

# TODO: Print state.model_dump() to verify the defaults:
# - steps should be 0
# - status should be "running"
# - pending_tool_calls should be an empty list
# - error and final_answer should be None
print(state.model_dump())