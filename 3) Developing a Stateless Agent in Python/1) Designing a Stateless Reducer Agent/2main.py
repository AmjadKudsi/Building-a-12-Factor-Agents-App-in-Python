import json
from core.agent import Agent

# Create an agent instance with default settings
agent = Agent()

# TODO: Print the agent.tool_schemas formatted with json.dumps
print(json.dumps(agent.tool_schemas, indent=2))