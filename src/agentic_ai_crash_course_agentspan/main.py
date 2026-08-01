from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


while True:
    query = input("Ask me anything: ")

    if query in ["/quit", "/q", "/bye", "/goodbye", "/end"]:
        break

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    print(f"Agentic AI: {response.output_text}")
