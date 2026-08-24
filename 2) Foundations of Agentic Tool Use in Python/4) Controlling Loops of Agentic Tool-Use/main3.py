import json
import openai

# Define the functions we want to make available to the model
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

# Define tool schemas including a special final_answer tool
tool_schemas = [
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
    },
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
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize context with the user's message
context = [
    {
        "role": "user",
        "content": "What is 15 + 27? Then multiply the result by 3."
    }
]

# Set up loop control variables
max_steps = 5
step = 0
done = False
final_answer = None

# Main agent loop: continue until done or max steps reached
while not done and step < max_steps:
    step += 1
    print(f"\n--- Step {step} ---")
    
    # Call the LLM with current context
    response = openai.responses.create(
        model="gpt-5",
        instructions=system_prompt,
        input=context,
        tools=tool_schemas,
        tool_choice="required",
        reasoning={"effort": "low"}
    )
    
    # Process each item in the response output
    for item in response.output:
        if item.type == "function_call":
            function_name = item.name
            args = json.loads(item.arguments)
            
            print(f"Calling function: {function_name}({args})")
            
            # TODO: Append the function call to context before executing any tool
            # Append a dict with: type="function_call", name=function_name, arguments=item.arguments, call_id=item.call_id
            context.append({
                "type": "function_call",
                "name": function_name,
                "arguments": item.arguments,
                "call_id": item.call_id
            })
            
            # TODO: Execute the requested tool inside a try/except using match on function_name
            # Handle "final_answer": set result to args.get("answer"), set final_answer to result, set output to json.dumps({"status": "reported"}), set done = True
            # Handle "add": call add(**args) and store in result, set output to json.dumps({"result": result})
            # Handle "multiply": call multiply(**args) and store in result, set output to json.dumps({"result": result})
            # Default case: set result to f"Tool {function_name} not found", set output to json.dumps({"error": result})
            # Except Exception as e: set result to f"Error: {e}", set output to json.dumps({"error": str(e)})
            try:
                match function_name:
                    case "final_answer":
                        result = args.get("answer")
                        final_answer = result
                        output = json.dumps({"status": "reported"})
                        done = True
                    
                    case "add":
                        result = add(**args)
                        output = json.dumps({"result": result})
                        
                    case "multiply":
                        result = multiply(**args)
                        output = json.dumps({"result": result})
                        
                    case _:
                        result = f"Tool {function_name} not found"
                        output = json.dumps({"error": result})
                        
            except Exception as e:
                result = f"Error: {e}"
                output = json.dumps({"error": str(e)})
            
            # TODO: Print the tool execution result for visibility
            print(f"Result: {result}")
            
            # TODO: Append the function_call_output back to context
            # Append a dict with: type="function_call_output", call_id=item.call_id, output=output
            context.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": output
            })
            
            # TODO: If done is True, break to stop further processing in the current iteration
            if done:
                break