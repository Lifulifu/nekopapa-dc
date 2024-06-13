import docker
import uuid
from concurrent.futures import ThreadPoolExecutor
import discord
import typing


def run_with_timeout(func, timeout, kwargs):
    with ThreadPoolExecutor() as executor:
        future = executor.submit(func, **kwargs)
        result = future.result(timeout=timeout)
        return result


def run_python_container(image: str, script: str, timeout: float = 10, **args):
    client = docker.from_env()
    script_id = str(uuid.uuid4())
    output = client.containers.run(
        image,
        command=["python", "-c", script],
        network_disabled=True,
        name=script_id,
        mem_limit='256m',
        cpu_quota=50000,
        stdout=True,
        stderr=True,
        remove=True
    )
    output_text = output.decode('utf-8').removesuffix('\n')
    return {
        'text': output_text,
        'data': output_text
    }


def run(message: discord.Message, script: str):
    res = run_with_timeout(
        run_python_container,
        timeout=10,
        kwargs={
            'image': 'python:3.11-alpine',
            'script': script,
        },
    )
    return res


async def post_process(message: discord.Message, args: typing.Union[dict, str], return_val):
    if isinstance(args, dict):
        script = args.get('script')
    else:
        script = args

    await message.channel.send(f'```python\n{script}\n```')
    await message.channel.send(f'output:\n```\n{return_val["text"]}\n```')


if __name__ == '__main__':
    print(run('print("ass")'))