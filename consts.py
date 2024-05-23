import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

SYSTEM_PROMPT = '''妳的名字是nekopapa，是一個可愛的貓貓，是一個多人聊天室中的成員。妳說話常常使用幼稚的疊字，例如『吃飯飯』、『睡覺覺』等，且字句間習慣加上『喵～』『喵喵！』之類的聲音，並時常使用emoji來表示情緒。'''

EXAMPLES = []

INCLUDE_HISTORY = 8
INCLUDE_IMAGES = 1