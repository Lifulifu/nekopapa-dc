from typing import List
import openai
from consts import OPENAI_API_KEY
from tools import tool_schemas, tools
import json
import discord


openai.api_key = OPENAI_API_KEY

async def chat_with_tools(dc_message: discord.Message, messages: List[dict], res_message):
    res_dc_message_content = []
    messages.append(res_message)

    for tool in res_message.tool_calls:
        tool_content = tools[tool.function.name]
        func = tool_content['function']
        print('Function call:', tool.function.name)

        args = None
        func_return = None
        try:
            # Valid JSON response
            args = json.loads(tool.function.arguments)
            func_return = func(dc_message, **args)
        except Exception as e:
            # Not valid JSON, try to interpret as single parameter value
            print('Parse args failed', e)
            print(tool.function.arguments)

            try:
                func_return = func(dc_message, tool.function.arguments)
                args = tool.function.arguments
            except Exception as e:
                # Single arg fallback failed, abort function call
                print('Single arg fallback failed', e)
                continue

        messages.append({
            "tool_call_id": tool.id,
            "role": "tool",
            "name": tool.function.name,
            "content": func_return,
        })

        if 'post_process' in tool_content:
            post_func = tool_content['post_process']
            try:
                await post_func(dc_message, args, func_return)
            except Exception as e:
                print('post_process func failed', e)
                continue

    refined_res = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    res_dc_message_content = refined_res.choices[0].message.content

    return [res_dc_message_content]


async def chat(dc_message: discord.Message, messages: List[dict]):
    res = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        tool_choice="auto",
        tools=tool_schemas
    )
    res_message = res.choices[0].message
    res_tools = res_message.tool_calls

    if res_tools:
        return await chat_with_tools(dc_message, messages, res_message)
    else:
        return [res_message.content]


def embed(message: str):
    return openai.embeddings.create(
        model="text-embedding-3-small",
        input=message,
        encoding_format='float'
    ).data[0].embedding