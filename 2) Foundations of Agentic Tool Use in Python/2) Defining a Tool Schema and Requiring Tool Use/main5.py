import json
import openai

# Define two tool schemas: final_answer and perform_math
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
    },
    {
        "type": "function",
        "name": "perform_math",
        "description": "Perform a mathematical calculation.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "The mathematical operation to perform."},
                "a": {"type": "number", "description": "The first number."},
                "b": {"type": "number", "description": "The second number."}
            },
            "required": ["operation", "a", "b"],
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
            "content": "Calculate 47 multiplied by 23 and give me the final answer."
        }
    ],
    tools=tool_schemas,
    tool_choice="required",
    reasoning={"effort": "low"}
)

# TODO: Write routing logic to handle different tool calls
for item in response.output:
    # TODO: Check if this is a function_call and route based on item.name
    # If item.name is "perform_math", print that the model requested a calculation
    if item.type == "function_call" and item.name == "perform_math":
        args = json.loads(item.arguments)
        print(f"Math request: {args['operation']} {args['a']} and {args['b']}")
        
        result = args["a"] * args["b"]
        print(f"Answer: {result}")
        
    # If item.name is "final_answer", parse arguments and print the answer
    elif item.type == "function_call" and item.name == "final_answer":
        args = json.loads(item.arguments)
        print(f"Answer: {args['answer']}")