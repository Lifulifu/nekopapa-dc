from typing import List
import openai
from consts import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def chat(messages: List[dict]):
    res = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    return res.choices[0].message.content