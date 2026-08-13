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
    tool_choice="required",
    reasoning={"effort": "low"}
)

# TODO: Write a for loop to iterate through response.output
    # TODO: Inside the loop, check if item.type is "function_call" and item.name is "final_answer"
        # TODO: Parse item.arguments using json.loads to convert the JSON string to a dictionary
        # TODO: Print the answer in the format: Answer: {args['answer']}
        
for item in response.output:
    if item.type == "function_call" and item.name == "final_answer":
        args = json.loads(item.arguments)
        print(f"Answer: {args['answer']}")