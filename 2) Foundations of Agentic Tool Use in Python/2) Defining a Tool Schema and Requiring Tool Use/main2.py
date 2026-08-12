import json
import openai

# Define a single tool schema for final_answer
tool_schemas = [
    {
        "type": "function",
        "name": "final_answer",
        "description": "Provide the final answer and stop.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The final answer for the user."}
            },
            "required": ["answer"],
            "additionalProperties": False
        }
    }
]

system_prompt = """
You are a helpful assistant.
"""

# Make a request to the Responses API
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "What is 15 + 27?"
        }
    ],
    tools=tool_schemas,
    # TODO: Add the tool_choice parameter and set it to "required" to enforce tool usage
    tool_choice="required",
    reasoning={"effort": "low"}
)

# Pretty-print the full response
print(json.dumps(response.model_dump(), indent=2))