from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

def generate_response(user_query):
    print(f"user response: {user_query}")
    response = client.responses.create(
        model="gpt-5-nano",
        input = f"{user_query}, keep response to 1 sentence"
    )
    print(response.output_text)
    return response.output_text