from core.agent import Agent

# Create an agent instance with extra instructions
agent = Agent(extra_instructions="Always show your work step by step.")

# Print the system prompt to verify it was loaded from file
print("System Prompt:")
print(agent.system_prompt)