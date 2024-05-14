from consts import SYSTEM_PROMPT, EXAMPLES, INCLUDE_HISTORY, INCLUDE_IMAGES
import discord
from openai_api import chat
import typing


def replace_user_ids(message: discord.Message):
    text = message.content
    for user in message.mentions:
        text = text.replace(f'<@{user.id}>', f'@{user.display_name}')
    return text


def process_response(res: str):
    return res.replace(f'nekopapa:', '').strip()


def construct_user_message(message: discord.Message, max_images: int = 1):
    content = []
    content.append({
        'type': 'text',
        'text': replace_user_ids(message)
    })

    used_images = 0
    for attachment in message.attachments:
        if attachment.content_type.startswith('image') and used_images < max_images:
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': attachment.url
                }
            })
            used_images += 1

    result = {
        'role': 'user',
        'name': str(message.author.id),
        'content': content
    }

    return result, used_images


async def handle(client: discord.Client, message: discord.Message, command: typing.List[str]=[]):
    raw_messages = []
    async for msg in message.channel.history(limit=INCLUDE_HISTORY):
        # Insert reply message
        raw_messages.append(msg)
        if msg.reference is not None:
            replied_message = await msg.channel.fetch_message(msg.reference.message_id)
            raw_messages.append(replied_message)

    # Construct input message history for response
    history = []
    total_used_images = 0
    for msg in raw_messages:
        if msg.author == client.user: # Is bot
            history.append({
                'role': 'assistant',
                'content': replace_user_ids(msg)
            })
        else:
            # INCLUDE_IMAGES will limit the amount of image in history, newest first
            user_message, used_images = construct_user_message(
                msg,
                max_images=INCLUDE_IMAGES - total_used_images
            )
            total_used_images += used_images
            history.append(user_message)

    history.reverse()

    input_messages = [
        { 'role': 'system', 'content': SYSTEM_PROMPT },
        *EXAMPLES,
        *history,
    ]
    print(input_messages)
    try:
        res = chat(input_messages)
        await message.channel.send(res)
    except Exception as e:
        print(e)
        await message.channel.send('發生錯誤，請聯絡 @lifu')

