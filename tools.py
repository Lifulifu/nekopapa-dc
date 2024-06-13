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
  'web_text_search': {
      'function': web_search.text_search,
      'post_process': web_search.text_search_post_process
  },
  'web_image_search': {
      'function': web_search.image_search,
      'post_process': web_search.image_search_post_process
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
                        'description': 'The python code to execute. **What you `print()` out is considered as the result, so you must use `print()` in your code.** Do not surround your code with markdown code block notation or any text that is not valid python code.\n## Example:\n\nresult = 69 + 42\nprint(result)'
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
            'name': 'web_text_search',
            'description': 'Input query string to perform web search with duckduckgo.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query string. You can use operators like `site:` to limit site and `+` `-` to include or exclude keywords.'
                    }
                },
                'required': ['query']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'web_image_search',
            'description': 'Input query string to perform image search with duckduckgo.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query string. You can use operators like `site:` to limit site and `+` `-` to include or exclude keywords.'
                    }
                },
                'required': ['query']
            }
        }
    }
]