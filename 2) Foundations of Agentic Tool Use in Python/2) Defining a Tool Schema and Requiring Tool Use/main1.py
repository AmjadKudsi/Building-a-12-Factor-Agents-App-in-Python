import json
import openai

# TODO: Complete the tool schema skeleton for final_answer
tool_schemas = [
    {
        "type": "function",  # TODO: set to "function"
        "name": "final_answer",  # TODO: set to "final_answer"
        "description": "Provide the final answer and stop.",  # TODO: describe what this tool does
        "strict": True,  # TODO: set to True to enforce schema adherence
        "parameters": {
            "type": "object",  # TODO: keep as "object" (tool args are an object)
            "properties": {  # TODO: define the "answer" field inside (type: string)
                "answer": {"type": "string", "description": "The final answer for the user."}
            },
            "required": ["answer"],  # TODO: include "answer"
            "additionalProperties": False # TODO: Set to False to disallow extra keys
        }
    }
]

# TODO: Clean this system prompt by removing the manual JSON instructions
# Keep only the persona definition
system_prompt = """
You are a helpful assistant.
"""

# TODO: Add the tools parameter with tool_schemas
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
    tool_choice="required",
    reasoning={"effort": "low"}
)

# Pretty-print the full response
print(json.dumps(response.model_dump(), indent=2))