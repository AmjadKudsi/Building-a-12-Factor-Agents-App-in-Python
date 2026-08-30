import json
from core.agent import Agent

# Create an agent instance with default settings
agent = Agent()

# Create a context with a simple user message
context = [
    {
        "role": "user",
        "content": "What is 5 + 3?"
    }
]

# TODO: Call agent._call_llm(context) and store the result in a variable called response
response = agent._call_llm(context)

# TODO: Use json.dumps(response.model_dump(), indent=2) to print the response
print(json.dumps(response.model_dump(), indent=2))