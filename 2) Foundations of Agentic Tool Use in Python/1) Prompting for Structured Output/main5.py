import json
import openai

# Define the system prompt that instructs the model on its behavior
system_prompt = """
You are a helpful assistant that only answers with the following JSON schema:
{
    "answer": "the answer to the question"
}
"""

# Make a request to the Responses API
# The input is a list of messages, starting with the user's question
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "What is 15 + 27?"
        }
    ],
    reasoning={"effort": "low"}
)

# Parse the output to extract the JSON answer
for item in response.output:
    # Check if this item is a message
    if item.type == "message":
        # TODO: Wrap the following code in a try block to handle JSON parsing errors
        try:
            # Extract raw text from the content
            text = item.content[0].text
            # Parse the JSON string from the content
            result = json.loads(text)
            # Extract and print the answer field
            print(f"Answer: {result['answer']}")
            
            # TODO: Add an except json.JSONDecodeError block here and print "Failed to parse JSON from response"
        except json.JSONDecodeError:
            print("Failed to parse JSON from response")
            