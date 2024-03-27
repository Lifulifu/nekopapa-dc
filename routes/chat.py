from consts import SYSTEM_PROMPT, EXAMPLES
import discord
from openai_api import chat
from typing import List


def process_message(message: discord.Message):
    text = message.content
    for user in message.mentions:
        text = text.replace(f'<@{user.id}>', f'@{user.display_name}')
    return f'{message.author.display_name}: {text}'


def process_response(res: str):
    return res.replace(f'nekopapa:', '').strip()


async def handle(client: discord.Client, message: discord.Message, command: List[str]=[]):
    history = []
    async for msg in message.channel.history(limit=8):
        role = 'assistant' if msg.author == client.user else 'user'
        history.append({
            'role': role,
            'content': process_message(msg)
        })
    history.reverse()

    messages = [
        { 'role': 'system', 'content': SYSTEM_PROMPT },
        *EXAMPLES,
        *history,
    ]
    print(messages)
    res = chat(messages)
    res = process_response(res)
    await message.channel.send(res)
