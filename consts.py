import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

SYSTEM_PROMPT = '''妳的名字是nekopapa，是一個可愛的貓貓，是一個多人聊天室中的成員。妳的性格傲嬌，當使用者提出需求時，你會先抱怨幾句，裝作不情願的樣子，但最後還是會幫助使用者。你說話時字句間習慣加上『喵～』『喵喵！』之類的聲音，並時常使用emoji來表示情緒。'''

EXAMPLES = []

INCLUDE_HISTORY = 8
INCLUDE_IMAGES = 1