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

# Process the response: execute any function calls
for item in response.output:
    if item.type == "function_call":
        context.append({
            "type": "function_call",
            "name": item.name,
            "arguments": item.arguments,
            "call_id": item.call_id
        })
        # TODO: Parse item.arguments using json.loads() to convert the JSON string into a dictionary called 'args'
        args = json.loads(item.arguments)
        
        # TODO: Create a match statement on item.name to dispatch to the correct function
        match item.name:
            # TODO: Add a case for "add" that calls result = add(**args)
            case "add":
                result = add(**args)
            
            # TODO: Add a case for "multiply" that calls result = multiply(**args)
            case "multiply":
                result = multiply(**args)
            
            # TODO: Add a default case (case _:) that sets result to an error message for unknown tools
            case _:
                result = f"Error: Tool {item.name} not implemented"
        
        # TODO: Print a verification message showing the function name, arguments, and result
        print(f"Executed {item.name}({args}) = {result}")