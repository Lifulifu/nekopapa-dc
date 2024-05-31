import discord
import json


def list_user_names(message: discord.Message):
    return json.dumps([
        member.display_name for member in message.channel.members
    ])


async def post_process(message: discord.Message, args, return_val):
    await message.channel.send(f'output:\n```{return_val}```')

