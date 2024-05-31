import discord
import typing
from qdrant_client import QdrantClient
from openai_api import chat, embed
from consts import MOCK_RESPONSE_SYSTEM_PROMPT
import re
import os


def remove_mentions(text: str):
    return re.sub(r'<@\d+>', '', text).strip()


async def handle(client: discord.Client, message: discord.Message, command: typing.List[str]=[]):
    if message.reference is None:
        await message.channel.send("沒有可以回覆的訊息")
        return

    message_to_react = await message.channel.fetch_message(message.reference.message_id)
    if not message_to_react.content:
        await message.channel.send("沒有可以回覆的訊息")
        return

    db = QdrantClient(url="http://localhost:6333")
    message_content = remove_mentions(message_to_react.content)
    mock_response = chat([
        {
            'role': 'system',
            'content': MOCK_RESPONSE_SYSTEM_PROMPT
        }, {
            'role': 'user',
            'content': message_content
        }
    ])[0]
    print('mock response:', mock_response)

    query_vector = embed(mock_response)
    search_result = db.search(
        collection_name="images",
        query_vector=query_vector,
        limit=1,
    )
    result = search_result[0].payload
    print('reaction image:', result['filename'])

    with open(os.path.join('images', result['filename']), 'rb') as f:
        file = discord.File(f)
        await message.channel.send(
            file=file,
            content=f'score: {search_result[0].score}',
            reference=message_to_react
        )



