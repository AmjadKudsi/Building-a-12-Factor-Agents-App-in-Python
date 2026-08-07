import openai
import json

# TODO: Make a request to the Responses API using openai.responses.create()
# Use model "gpt-5", provide an input list with a user message, and set reasoning to {"effort": "low"}
response = openai.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": "What is the square root of 2?"
        }
    ],
    reasoning={"effort": "low"}
)

# TODO: Loop through response.output
    # TODO: Check if item.type equals "message"
        # TODO: Extract the text by accessing item.content[0].text
        # TODO: Print the text
for item in response.output:
    if item.type == "message":
        text = item.content[0].text        
        print(f"Answer: {text}")        