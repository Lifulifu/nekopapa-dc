import py_executor
import dc_utils
import web_search

tools = {
  'run_python': {
      'function': py_executor.run,
      'post_process': py_executor.post_process
  },
  'list_user_names': {
      'function': dc_utils.list_user_names,
      'post_process': dc_utils.post_process
  },
  'web_search': {
      'function': web_search.search,
      'post_process': web_search.post_process
  }
}

tool_schemas = [
    {
        'type': 'function',
        'function': {
            'name': 'run_python',
            'description': 'Run python script and get result by printing to stdout.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'script': {
                        'type': 'string',
                        'description': 'The python code to execute. Gets results via stdout. This parameter accepts purely python code as string, do not surround your code with markdown code block notation or any text that is not valid python code.\n## Example:\n\nresult = 69 + 42\nprint(result)'
                    },
                },
                'required': ['script'],
            },
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_user_names',
            'description': 'List all users in the chat room.',
            'parameters': {},
            'required': []
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'web_search',
            'description': 'Input query string to perform web search with duckduckgo.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query string. You can use operators like `site:` to limit site and `+` `-` to include or exclude keywords.'
                    }
                },
                'required': []
            }
        }
    }
]