from duckduckgo_search import DDGS
import discord
import typing
import aiohttp
import io


async def send_image_with_url(message: discord.Message, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img = await resp.read()
            with io.BytesIO(img) as file:
                await message.channel.send(file=discord.File(file, "image.png"))


def text_search(message: discord.Message, query: str):
    res = DDGS().text(query, max_results=3)
    return {
        'data': res,
        'text': '\n---\n'.join([ f'{r["title"]}\n{r["body"]}' for r in res ])
    }


async def text_search_post_process(message: discord.Message, args: typing.Union[dict, str], return_val: dict):
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


def image_search(message: discord.Message, query: str):
    res = DDGS().images(query, max_results=2)
    return {
        'data': res,
        'text': 'Image search result and sources has been sent, do not further send links.'
    }


async def image_search_post_process(message: discord.Message, args: typing.Union[dict, str], return_val: dict):
    if isinstance(args, dict):
        query = args.get('query')
    else:
        query = args

    try:
        await message.channel.send(f'query:\n```\n{query}\n```')
        for res in return_val['data']:
            await message.channel.send(f'[src]({res["url"]})')
            await send_image_with_url(message, res['image'])
    except Exception as e:
        print(f'parse return_val failed in post_process: {e}')
        print(return_val)