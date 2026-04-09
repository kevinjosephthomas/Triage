from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_advice(user_data, risk):
    prompt = f"""
    You are a medical triage assistant.

    Patient details:
    {user_data}

    Predicted risk level: {risk}

    Explain the condition and give simple advice.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content