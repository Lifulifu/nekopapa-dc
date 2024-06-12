from duckduckgo_search import DDGS
import discord
import typing


def search(message: discord.Message, query: str):
    return DDGS().text(query, max_results=3)


async def post_process(message: discord.Message, args: typing.Union[dict, str], return_val: typing.List):
    if isinstance(args, dict):
        query = args.get('query')
    else:
        query = args

    results = '\n'.join([ f'[{res["title"]}]({res["href"]})' for i, res in enumerate(return_val) ])

    await message.channel.send(f'query:\n```{query}```')
    await message.channel.send(f'result:\n{results}')