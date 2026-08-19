import json
import openai

# Define the functions we want to make available to the model
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

# Define tool schemas for the model (including final_answer)
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
        "name": "add",
        "description": "Add two numbers together",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "multiply",
        "description": "Multiply two numbers together",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    }
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize context with the user's message
context = [
    {
        "role": "user",
        "content": "Compute 15 + 27"
    }
]

# First API call: the model will see the user's request and available tools
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=context,
    tools=tool_schemas,
    tool_choice="required",
    reasoning={"effort": "low"}
)

# Process the response: execute any function calls and add results to context
for item in response.output:
    if item.type == "function_call":
        # TODO: Append the function call to context as a dictionary with four fields:
        # "type" (set to "function_call"), "name" (item.name), "arguments" (item.arguments), 
        # and "call_id" (item.call_id)
        context.append({
            "type": "function_call",
            "name": item.name,
            "arguments": item.arguments,
            "call_id": item.call_id
        })
        
        # Step 2: Execute the function call using a match statement
        args = json.loads(item.arguments)
        
        match item.name:
            case "add":
                result = add(**args)
            case "multiply":
                result = multiply(**args)
            case _:
                result = f"Error: Tool {item.name} not implemented"
        
        print(f"Executed {item.name}({args}) = {result}")
        
        # TODO: Append the function result to context as a dictionary with three fields:
        # "type" (set to "function_call_output"), "call_id" (same as the function call's call_id),
        # and "output" (use json.dumps to serialize {"result": result})
        context.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({"result": result})
        })

# TODO: Print a blank line, then print "Current context:", then print the entire context list
# using json.dumps(context, indent=2) to format it nicely
print("\nCurrent context:")
print(json.dumps(context, indent=2))