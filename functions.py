import time
import random
import requests
from output import say, engine
import speech_recognition as sr
# import openai
from key import key
from translate import Translator

def get_time(text:str):
    current_time = time.localtime()
    output_time = f'{current_time.tm_hour}:{current_time.tm_min}' 
    return {"время":output_time}

def get_random_number(text:str):
    return {"число": random.randint(0,100)}

def get_random_flip(text:str):
    variants = ["орел", "решка"]
    winner = random.choice(variants)
    if winner == "орел":
        return {"сторона_победитель": "орел", "сторона_проигравший": "решка"}
    else:
        return {"сторона_победитель": "решка", "сторона_проигравший": "орел"}
    
def get_dollar_currency(text:str):
    result = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
    result = result.json()
    total = str(round(float(result[1]['sale']),2))
    total = total.split('.')
    return {"курс_грн": total[0], "курс_копейка": total[1]}
# 

def game(text:str):
    recognizer = sr.Recognizer()
    say("Хорошо давай сыграем, я загадал число от 1 до 100 твоя задача его отгадать, скажи конец если захочешь закончить игру")
    correct_number = random.randint(0,100)
    with sr.Microphone() as source:
        print('ready game')
        while True:
            engine.runAndWait()
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            try:
                text = recognizer.recognize_google(audio, language='ru-RU')
                print(f"Вы сказали: {text}")
                if text.isdigit():
                    number_user = int(text)
                    if number_user == correct_number:
                        say("Поздравляю, ты угадал.")
                        break
                    elif number_user < correct_number:
                        say(f"Попробуй еще раз, мое число больше {number_user}")
                    elif number_user > correct_number:
                        say(f"Попробуй еще раз, мое число меньше {number_user}")
                elif "конец" in text:
                    break
                else:
                    say("Скажите только число, ничего лишнего")
            except sr.UnknownValueError:
                print("Не удалось распознать звук")
            except sr.RequestError:
                print("request error")
            except sr.WaitTimeoutError:
                print("wait timeout")
    return {}

# def ai(text:str):
                        
#     prompt = f'''Ты должен генерировать ответы для голосового помощника, без лишнего текста,
#     все что ты сгенерируешь я буду сразу отправлять пользователю в виде звука
#     давай КРАТКИЕ ответы не надо полностью раскрывать тему
#     Ниже предоставляю то что спрашивает пользователь

#     {text}
#     '''
#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return {"текст":response["choices"][0]["message"]['content'].strip()}

def ai(text: str):
    translator = Translator(to_lang="en")
    translated_text = translator.translate(text)

    API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-3B"
    headers = {"Authorization": f"Bearer {key}"}

    prompt = f"User: {translated_text}\nAI:"

    payload = {"inputs": prompt, "parameters": {"max_length": 150, "temperature": 0.5}}
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}, текст ответа: {response.text}")
        return {"текст": "Произошла ошибка при обращении к AI"}

    response_json = response.json()
    print(f"Ответ от API: {response_json}")  # Друк для відладки

    if isinstance(response_json, list) and len(response_json) > 0 and "generated_text" in response_json[0]:
        ai_response = response_json[0]["generated_text"].strip()
        translator = Translator(to_lang="ru")  # Оновимо мову перекладу на російську
        translated_response = translator.translate(ai_response)
        return {"текст": translated_response}
    else:
        print(f"Unexpected response format: {response_json}")
        return {"текст": "Не удалось получить ответ от AI"}
