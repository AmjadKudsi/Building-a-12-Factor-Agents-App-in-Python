import json
from core.agent import Agent

# Create an agent instance with default settings
agent = Agent()

# Create a context with a message that prompts the model to call final_answer directly
# We ask for a direct answer to encourage the model to use final_answer without needing math tools
context = [
    {
        "role": "user",
        "content": "Please provide your final answer now and stop. Just say 'Hello, I am ready!'"
    }
]

# TODO: Call agent._next_step(context) and capture the three return values in variables:
#   updated_context, status, final_answer
updated_context, status, final_answer = agent._next_step(context)

# TODO: Print the status (expected: "complete")
print(status)

# TODO: Print the final_answer (expected: a string containing the model's response)
print(final_answer)

# TODO: Print how many items are in updated_context (hint: use len())
print(len(updated_context))