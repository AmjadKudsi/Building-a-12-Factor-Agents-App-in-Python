import json
import openai

# Define the system prompt that instructs the model on its behavior
system_prompt = """
You are a helpful assistant that only answers with the following JSON schema:
{
    "tasks": ["task1", "task2", "task3"]
}

Where "tasks" is a list of tasks extracted from the user's message.
"""

# Make a request to the Responses API
# The input is a list of messages, starting with the user's natural language todo list
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "I need to buy milk, walk the dog, and call mom"
        }
    ],
    reasoning={"effort": "low"}
)

# Parse the output to extract the JSON tasks
for item in response.output:
    # Check if this item is a message
    if item.type == "message":
        try:
            # Extract raw text from the content
            text = item.content[0].text
            # Parse the JSON string from the content
            result = json.loads(text)
            # TODO: Loop through each task in result['tasks'] and print it
            for task in result['tasks']:
                print(f"- {task}")

        except json.JSONDecodeError:
            # Handle cases where the model didn't return valid JSON
            print("Failed to parse JSON from response")