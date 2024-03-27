import discord

async def handle(client: discord.Client, message: discord.Message, command: list=[]):
    await message.channel.send('pong')