from py_executor import run_python

tools = {
  'run_python': {
      'function': run_python,
  }
}

tool_schemas = [
  {
    "type": "function",
    "function": {
      "name": "run_python",
      "description": "Run python script and get result by printing to stdout.",
      "parameters": {
        "type": "object",
        "properties": {
          "script": {
            "type": "string",
            "description": "The python code to execute. Gets results via stdout. This parameter accepts purely python code as string, do not surround your code with markdown code block notation or any text that is not valid python code.\n## Example:\n\nresult = 69 + 42\nprint(result)"
          },
        },
        "required": ["script"],
      },
    }
  }
]