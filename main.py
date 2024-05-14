from consts import DISCORD_TOKEN
import discord
import routes
from manager import CommandManager, ThreadManager

intents: discord.Intents = discord.Intents.all()
client = discord.Client(intents=intents)

command_manager = CommandManager(client)
command_manager.register('ping', routes.ping.handle)
command_manager.register('game', routes.game.handle_start)
command_manager.register('leaderboard', routes.game.handle_leaderboard)
command_manager.register(CommandManager.DEFAULT_ROUTE, routes.chat.handle)

thread_manager = ThreadManager(client)
thread_manager.register('Game', routes.game.handle_play)

@client.event
async def on_ready():
    print(f'{client.user} is running...')


@client.event
async def on_message(message: discord.Message):
    # Is bot talking, avoid infinite trigger
    if message.author == client.user:
        return

    # Is in game thread
    if message.channel.type == discord.ChannelType.public_thread and message.channel.owner == client.user:
        await thread_manager.handle(message)
    # Trigger only if bot is mentioned
    elif client.user in message.mentions:
        await command_manager.handle(message)


if __name__ == '__main__':
    routes.game.init_db()

    client.run(DISCORD_TOKEN)