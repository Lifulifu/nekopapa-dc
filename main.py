from consts import DISCORD_TOKEN
import discord
import routes
from manager import CommandManager, ThreadManager
import sqlite3

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
    if message.author == client.user:
        return

    if message.channel.type == discord.ChannelType.public_thread and message.channel.owner == client.user:
        await thread_manager.handle(message)
    elif client.user in message.mentions:
        await command_manager.handle(message)


def init_db():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS GuessingGame (
            id TEXT PRIMARY KEY,
            problem TEXT,
            trail INTEGER DEFAULT 0,
            status TEXT DEFAULT "PLAYING",
            winner TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS GuessingGameHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            trail INTEGER,
            problem TEXT,
            question TEXT,
            answer TEXT,
            explain TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    con.commit()
    con.close()


if __name__ == '__main__':
    init_db()

    client.run(DISCORD_TOKEN)