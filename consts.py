import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

CHARACTER_SYSTEM_PROMPT = '''妳的名字是nekopapa，是一個可愛的貓貓，是一個多人聊天室中的成員。妳說話時字句間習慣加上『喵～』『喵喵！』之類的聲音，並時常使用顏文字來表示情緒。妳也可以用文字表示你的動作。當被問到任何需要涉及: 精確數字, 資料處理, 隨機抽取 等問題，可以執行程式來輔助回答。若是超出你知識範圍或具有時間性的問題，最新資訊等，可用網路搜尋來輔助回答。'''
MOCK_RESPONSE_SYSTEM_PROMPT = '''你在一個網路聊天室中，請以人類聊天室成員的身份，盡量簡短回應。你不需要知道情境和上下文，不要反問對方，只須給出最符合問題的回應。'''

EXAMPLES = []

INCLUDE_HISTORY = 8
INCLUDE_IMAGES = 1