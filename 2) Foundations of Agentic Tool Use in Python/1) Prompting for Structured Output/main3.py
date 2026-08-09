import openai
import json

# Define the system prompt that instructs the model on its behavior
system_prompt = """
You are a helpful City Guide assistant that only answers with the following JSON schema:
{
    "city": "the name of the city",
    "country": "the country where the city is located",
    "population": "the population of the city"
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
            "content": "Tell me about Tokyo"
        }
    ],
    reasoning={"effort": "low"}
)

# Parse the output to extract the JSON answer
for item in response.output:
    # Check if this item is a message
    if item.type == "message":
        # Extract raw text from the content
        text = item.content[0].text
        # You now have the JSON string in the text variable!
        
        # TODO: Import the json library at the top of this file
        
        # TODO: Parse the JSON string into a Python dictionary using json.loads()
        
        # TODO: Print the city field from the result dictionary
        
        # TODO: Print the country field from the result dictionary
        
        # TODO: Print the population field from the result dictionary
        
        result = json.loads(text)
        print(f"City: {result['city']}")
        print(f"Country: {result['country']}")
        print(f"Population: {result['population']}")
        