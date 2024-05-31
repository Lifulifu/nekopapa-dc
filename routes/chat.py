from consts import CHARACTER_SYSTEM_PROMPT, EXAMPLES, INCLUDE_HISTORY, INCLUDE_IMAGES
import discord
from openai_api import chat
import typing
import re


def replace_user_ids(message: discord.Message):
    text = message.content
    for user in message.mentions:
        text = text.replace(f'<@{user.id}>', f'@{user.display_name}')
    return text


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

    return result


async def handle(client: discord.Client, message: discord.Message, command: typing.List[str]=[]):
    history = []
    is_newest_message = True
    async for msg in message.channel.history(limit=INCLUDE_HISTORY):
        if re.match(f'^<@{client.user.id}>\s*clear$', msg.content): # Don't further append history
            break

        if msg.author == client.user: # Is bot
            history.append({
                'role': 'assistant',
                'content': replace_user_ids(msg)
            })
        else:
            # Only include images in the most recent message
            max_images = INCLUDE_IMAGES if is_newest_message else 0
            user_message = construct_user_message(msg, max_images=max_images)
            history.append(user_message)

            if msg.reference is not None:
                try:
                    replied_message = await msg.channel.fetch_message(msg.reference.message_id)
                    replied_message = construct_user_message(replied_message, max_images=max_images)
                    history.append(replied_message)
                except Exception as e:
                    print('Cannot find reference message', e)

        is_newest_message = False

    history.reverse()

    input_messages = [
        { 'role': 'system', 'content': CHARACTER_SYSTEM_PROMPT },
        *EXAMPLES,
        *history,
    ]
    print(input_messages)

    try:
        res = await chat(message, input_messages)
        for r in res:
            await message.channel.send(r)
    except Exception as e:
        print(e)
        await message.channel.send('發生錯誤，請聯絡 @lifu')