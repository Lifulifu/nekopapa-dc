from duckduckgo_search import DDGS
import discord
import typing
import json


def search(message: discord.Message, query: str):
    res = DDGS().text(query, max_results=3)
    return {
        'data': res,
        'text': '\n---\n'.join([ f'{r["title"]}\n{r["body"]}' for r in res ])
    }


async def post_process(message: discord.Message, args: typing.Union[dict, str], return_val: str):
    if isinstance(args, dict):
        query = args.get('query')
    else:
        query = args

    try:
        return_val = return_val['data']
        results = '\n'.join([ f'[{res["title"]}]({res["href"]})' for res in return_val ])
        await message.channel.send(f'query:\n```\n{query}\n```')
        await message.channel.send(f'result:\n{results}')
    except Exception as e:
        print(f'parse return_val failed in post_process: {e}')
        print(return_val)
