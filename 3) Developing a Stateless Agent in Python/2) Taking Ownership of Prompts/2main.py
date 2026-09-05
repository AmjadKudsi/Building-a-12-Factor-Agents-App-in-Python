from core.utils.context_serializer import serialize_context_to_text

# Build a minimal context with one user message and no tool calls
context = [
    {
        "role": "user",
        "content": "Calculate the sum of 42 and 58"
    }
]

# TODO: Serialize and print the formatted output
formatted_context = serialize_context_to_text(context)
print(formatted_context)