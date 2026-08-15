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
                "answer": {"type": "string", "description": "The final answer for the user."},
                # TODO: Add a "confidence" property with type "number" and description "A score between 0 and 100 indicating confidence in the answer."
                "confidence": {"type": "number", "description": "A score between 0 and 100 indicating confidence in the answer"}
            },
            # TODO: Add "confidence" to the required list below
            "required": ["answer", "confidence"],
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
    tool_choice="required",
    reasoning={"effort": "low"}
)

# The model returns a function_call item with JSON arguments
for item in response.output:
    if item.type == "function_call" and item.name == "final_answer":
        args = json.loads(item.arguments)
        print(f"Answer: {args['answer']}")
        # TODO: Extract and print the confidence value in a similar format
        print(f"Confidence Score: {args['confidence']}")