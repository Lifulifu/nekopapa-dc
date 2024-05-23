from consts import DISCORD_TOKEN
import discord
from discord.ext import commands
import routes
from manager import CommandManager, ThreadManager

intents: discord.Intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

command_manager = CommandManager(bot)
command_manager.register('ping', routes.ping.handle)
command_manager.register('game', routes.game.handle_start)
command_manager.register('leaderboard', routes.game.handle_leaderboard)
command_manager.register('clear', None)
command_manager.register(CommandManager.DEFAULT_ROUTE, routes.chat.handle)

thread_manager = ThreadManager(bot)
thread_manager.register('Game', routes.game.handle_play)

@bot.event
async def on_ready():
    print(f'{bot.user} is running...')
    await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    # Is bot talking, avoid infinite trigger
    if message.author == bot.user:
        return

    # Is in game thread
    if message.channel.type == discord.ChannelType.public_thread and message.channel.owner == bot.user:
        await thread_manager.handle(message)
    # Trigger only if bot is mentioned
    elif bot.user in message.mentions:
        await command_manager.handle(message)


if __name__ == '__main__':
    routes.game.init_db()

    bot.run(DISCORD_TOKEN)