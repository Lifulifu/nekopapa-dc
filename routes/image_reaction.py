import discord
import typing
from qdrant_client import QdrantClient
from openai_api import embed


async def handle(client: discord.Client, message: discord.Message, command: typing.List[str]=[]):
    if message.reference is None:
        await message.channel.send("沒有可以回覆的訊息")
        return

    message_to_react = await message.channel.fetch_message(message.reference.message_id)
    if not message_to_react.content:
        await message.channel.send("沒有可以回覆的訊息")
        return

    db = QdrantClient(url="http://localhost:6333")
    query_vector = embed(message_to_react.content)
    search_result = db.search(
        collection_name="images",
        query_vector=query_vector,
        limit=1,
    )
    result = search_result[0].payload
    with open(result['filename'], 'rb') as f:
        print('reaction image:', result['filename'])
        file = discord.File(f)
        await message.channel.send(file=file)



