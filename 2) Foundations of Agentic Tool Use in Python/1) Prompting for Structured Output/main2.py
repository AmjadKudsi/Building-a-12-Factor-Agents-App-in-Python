import openai

# TODO: Define a system_prompt variable with a triple-quoted string
# TODO: Instruct the model to only answer with the following JSON schema
# TODO: Show a JSON template with "category" and "brand" fields
system_prompt = """
You are a product categorizer.

Only answer with the following JSON schema:

{
    "category": "The general product category, such as Electronics or Clothing",
    "brand": "The brand name of the product"
}

Do not include any additional text, explanation, or Markdown.
Return only the JSON object.
"""

# Make a request to the Responses API
response = openai.responses.create(
    model="gpt-5",
    # TODO: Add the instructions parameter with system_prompt as its value
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "Tell me about the iPhone 15 Pro"
        }
    ],
    reasoning={"effort": "low"}
)

# Loop through the response output
for item in response.output:
    # Check if this item is a message
    if item.type == "message":
        # Extract the text from the nested structure
        text = item.content[0].text
        # Print the result
        print(text)