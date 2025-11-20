from zai import ZaiClient

client = ZaiClient(api_key="437ddc42024540289340856f79ed78d6.rQ5IssIhSkaCAsTJ")  # Your API Key

response = client.chat.completions.create(
    model="glm-4.5",
    messages=[
        {"role": "user", "content": "As a marketing expert, please create an attractive slogan for my product."},
        {"role": "assistant", "content": "Sure, to craft a compelling slogan, please tell me more about your product."},
        {"role": "user", "content": "Z.AI Open Platform"}
    ],
    thinking={
        "type": "enabled",
    },
    max_tokens=4096,
    temperature=0.6
)

# Get complete response
print(response.choices[0].message)