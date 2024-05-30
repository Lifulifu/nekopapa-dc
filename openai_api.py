from typing import List
import openai
from consts import OPENAI_API_KEY
from tools import tool_schemas, tools
import json


openai.api_key = OPENAI_API_KEY

def chat_with_tools(messages: List[dict], res_message):
    res_dc_messages = []
    messages.append(res_message)

    for tool in res_message.tool_calls:
        func = tools[tool.function.name]['function']

        args = None
        arg_val = None
        func_response = None
        try:
            # Valid JSON response
            args = json.loads(tool.function.arguments)
            err, func_response = func(**args)
        except Exception as e:
            # Not valid JSON, try to interpret as single parameter value
            print('Parse args failed', e)
            print(tool.function.arguments)

            try:
                err, func_response = func(tool.function.arguments)
                arg_val = tool.function.arguments
            except Exception as e:
                # Single arg fallback failed, abort function call
                print('Single arg fallback failed', e)
                continue

        if err is None:
            messages.append({
                "tool_call_id": tool.id,
                "role": "tool",
                "name": tool.function.name,
                "content": func_response,
            })

            if tool.function.name == 'run_python':
                res_dc_messages.append(
                    f'```python\n{arg_val if arg_val is not None else args.get("script") }\n```'
                )
                res_dc_messages.append(
                    f'output:\n```{func_response}```'
                )

    refined_res = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    res_dc_messages.append(refined_res.choices[0].message.content)

    return res_dc_messages


def chat(messages: List[dict]):
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
        return chat_with_tools(messages, res_message)
    else:
        return [res_message.content]


def embed(message: str):
    return openai.embeddings.create(
        model="text-embedding-3-small",
        input=message,
        encoding_format='float'
    ).data[0].embedding