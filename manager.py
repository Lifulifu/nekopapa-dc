import discord
from typing import Callable
import re

class CommandManager:
    DEFAULT_ROUTE = '*'

    def __init__(self, client: discord.Client):
        self.client = client
        self.routes = {}

    def register(self, name: str, handler: Callable):
        self.routes[name] = handler

    def parse_command(self, message: discord.Message):
        return [text.strip() for text in message.content.split(' ')]

    async def handle(self, message: discord.Message):
        commands = self.parse_command(message)
        command = commands[1] if len(commands) >= 2 else None

        if command == 'help':
            text = '\n'.join([name for name in self.routes.keys() if name != self.DEFAULT_ROUTE])
            await message.channel.send(f'```Available commands: \n\n{text}```')
        elif command in self.routes:
            await self.routes[command](self.client, message, command)
        else:
            await self.routes[self.DEFAULT_ROUTE](self.client, message, command)


class ThreadManager:
    def __init__(self, client: discord.Client):
        self.client = client
        self.routes = {}

    def register(self, name: str, handler: Callable):
        self.routes[name] = handler

    def parse_channel(self, message: discord.Message):
        if not message.channel.type == discord.ChannelType.public_thread:
            raise Exception('The message is not in a thread')

        route = re.match(r'^\[(\w+)\]', message.channel.name)
        if route is None:
            raise Exception('Thread name is not in the correct format')
        return route.group(1)

    async def handle(self, message: discord.Message):
        channel = self.parse_channel(message)
        await self.routes[channel](self.client, message)