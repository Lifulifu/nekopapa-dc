import docker
import uuid
from concurrent.futures import ThreadPoolExecutor


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
    return output_text


def run_python(script: str):
    try:
        res = run_with_timeout(
            run_python_container,
            timeout=10,
            kwargs={
                'image': 'python:3.11-alpine',
                'script': script,
            },
        )
        return None, res
    except Exception as e:
        return e, None


if __name__ == '__main__':
    print(run_python('print("ass")'))