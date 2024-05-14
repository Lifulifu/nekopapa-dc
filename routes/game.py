from routes.chat import chat
import random
import pypinyin
import discord
import sqlite3
import json
from tabulate import tabulate

con = sqlite3.connect('db/main.db')

answerer_messages = [
    {
        'role': 'system',
        'content': '''你主持一個叫『猜東西』的文字遊戲，在這個遊戲中會有一個玩家不知道的『東西』(subject)，玩家藉由詢問是非題來猜出『東西』是什麼。玩家會用function call的形式來問問題: `ask(subject: string, question: string)`，你必須依據常識判斷在大部分情況下該敘述是否為真，並返回你的解釋以及回答，輸出為陣列形式：`[<解釋>, <回答>]`。

請注意，你必須判斷玩家的問題是否能以 "TRUE" / "FALSE" 回答，如果問題不是是非題或問題模糊，則應輸出 "ERROR"。'''
    }, {
        'role': 'user',
        'content': 'ask("蘋果", "這個東西是動物嗎？")'
    }, {
        'role': 'assistant',
        'content': '["蘋果屬於植物而非動物", "FALSE"]'
    }, {
        'role': 'user',
        'content': 'ask("馬車", "是人造物嗎")'
    }, {
        'role': 'assistant',
        'content': '["馬車是人造物", "TRUE"]'
    }, {
        'role': 'user',
        'content': 'ask("蘋果", "它是什麼顏色的")'
    }, {
        'role': 'assistant',
        'content': '["問題無法以TRUE/FALSE回答", "ERROR"]'
    }, {
        'role': 'user',
        'content': 'ask("警察", "是動物嗎")'
    }, {
        'role': 'assistant',
        'content': '["警察通常是人類，而人類是一種動物", "TRUE"]'
    }, {
        'role': 'user',
        'content': 'ask("雞腿", "是動物嗎")'
    }, {
        'role': 'assistant',
        'content': '["無法明確判斷動物的身體部位是否能被定義為動物", "ERROR"]'
    }
]

def init_db():
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS GuessingGame (
            id TEXT PRIMARY KEY,
            problem TEXT,
            trail INTEGER DEFAULT 0,
            status TEXT DEFAULT "PLAYING",
            winner TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS GuessingGameHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            trail INTEGER,
            problem TEXT,
            question TEXT,
            answer TEXT,
            explain TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    con.commit()
    con.close()


def get_problem():
    with open('./problems.txt', 'r') as f:
        problems = f.readlines()
    return random.choice(problems).strip()


def get_problem_info(problem: str):
    return f'題目有 {len(problem)} 個字，第一個注音符號是 {pypinyin.pinyin(problem, style=pypinyin.BOPOMOFO)[0][0][0]}'


def ask(problem: str, message: str):
    res = chat([
        *answerer_messages,
        {'role': 'user', 'content': f'ask("{problem}", "{message}"'}
    ])
    return json.loads(res)


def get_game_history(game_id: str, chunk_size=5):
    cur = con.cursor()
    res = cur.execute('SELECT timestamp, problem, trail, question, answer, explain FROM GuessingGameHistory WHERE game_id = ?', (game_id,))
    res = res.fetchall()

    # sort by timestamp
    res.sort(key=lambda x: x[0])

    result = []
    texts = []
    for i, (_, problem, trail, question, answer, explain) in enumerate(res):
        if answer == 'WRONGANS':
            texts.append(f'[問題 {trail}]\n猜：{question[1:].strip()}\n錯誤答案')
        elif answer == 'RIGHTANS':
            texts.append(f'[問題 {trail}]\n猜：{question[1:].strip()}\n正確答案')
        else:
            texts.append(f'[問題 {trail}]\n問：{question}\n答：{answer}\n解釋：{explain}')

        if i % chunk_size == chunk_size-1:
            result.append('\n\n'.join(texts))
            texts = []

    if len(texts) > 0: result.append('\n\n'.join(texts))
    return result


def get_game_leaderboard(client: discord.Client):
    cur = con.cursor()
    res = cur.execute('SELECT winner, trail, problem FROM GuessingGame WHERE status = "WIN" ORDER BY trail ASC LIMIT 10')
    res = res.fetchall()

    header = ['排名', '玩家', '題目', '使用題數']
    data = []
    for i, (winner, trail, problem) in enumerate(res):
        display_name = client.get_user(int(winner)).display_name
        data.append([i+1, display_name, problem, trail])

    return f'```\n{tabulate(data, headers=header, tablefmt="simple")}\n```'


async def handle_start(client: discord.Client, message: discord.Message, command: list=[]):
    thread = await message.channel.create_thread(name='[Game] 猜東西', type=discord.ChannelType.public_thread)
    problem = get_problem()

    cur = con.cursor()
    cur.execute(
        '''INSERT INTO GuessingGame (id, problem, trail) VALUES (?, ?, ?)''',
        (thread.id, problem, 0)
    )
    con.commit()

    await thread.send(f'遊戲開始！\n輸入 `={{你的答案}}` 回答問題，或輸入 `=` 放棄作答\n\n{get_problem_info(problem)}')


async def handle_play(client: discord.Client, message: discord.Message, command: list=[]):
    cur = con.cursor()
    res = cur.execute('SELECT problem, trail, status FROM GuessingGame WHERE id = ?', (message.channel.id,))
    res = res.fetchone()
    if res is None: await message.channel.send(f'找不到此遊戲')
    problem, trail, status = res

    if status != 'PLAYING':
        await message.channel.send(f'遊戲已結束')
        return

    # user try to answer
    if message.content.startswith('='):
        answer = message.content[1:].strip()
        if answer == '':
            cur.execute('UPDATE GuessingGame SET status = ? WHERE id = ?', ('GIVEUP', message.channel.id))
            await message.channel.send(f'已放棄遊戲。\n答案是『{problem}』\n\n你問了 {trail} 個問題')
            history = get_game_history(message.channel.id)
            for chunk in history: await message.channel.send(f'遊戲紀錄：\n```\n{chunk}\n```')
        elif answer == problem:
            await message.channel.send(f'答對了！\n答案是『{problem}』\n\n你問了 {trail} 個問題')
            cur.execute('UPDATE GuessingGame SET status = ?, winner = ? WHERE id = ?', ('WIN', message.author.id, message.channel.id))
            cur.execute(
                'INSERT INTO GuessingGameHistory (game_id, problem, trail, question, answer, explain) VALUES (?, ?, ?, ?, ?, ?)',
                (message.channel.id, problem, trail+1, message.content, 'RIGHTANS', '')
            )
            history = get_game_history(message.channel.id)
            for chunk in history: await message.channel.send(f'遊戲紀錄：\n```\n{chunk}\n```')
        else:
            await message.channel.send(f'答錯了。\n\n你問了 {trail} 個問題\n{get_problem_info(problem)}')
            cur.execute(
                'INSERT INTO GuessingGameHistory (game_id, problem, trail, question, answer, explain) VALUES (?, ?, ?, ?, ?, ?)',
                (message.channel.id, problem, trail, message.content, 'WRONGANS', '')
            )
        con.commit()
        return

    # user ask question
    try:
        explain, answer = ask(problem, message.content)
    except Exception as e:
        await message.channel.send(f'發生錯誤')
        print(e)
        return

    problem_info = get_problem_info(problem)
    match answer:
        case 'TRUE':
            trail += 1
            await message.channel.send(f'是\n\n你問了 {trail} 個問題\n{problem_info}')
        case 'FALSE':
            trail += 1
            await message.channel.send(f'否\n\n你問了 {trail} 個問題\n{problem_info}')
        case 'ERROR':
            await message.channel.send(f'無法判斷\n\n你問了 {trail} 個問題\n{problem_info}')

    # write history to db
    cur.execute('''
        INSERT INTO GuessingGameHistory (game_id, problem, trail, question, answer, explain) VALUES (?, ?, ?, ?, ?, ?)''',
        (message.channel.id, problem, trail, message.content, answer, explain))

    # update trail
    cur.execute('UPDATE GuessingGame SET trail = ? WHERE id = ?', (trail, message.channel.id))
    con.commit()


async def handle_leaderboard(client: discord.Client, message: discord.Message, command: list=[]):
    await message.channel.send(get_game_leaderboard(client))