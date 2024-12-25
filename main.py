import speech_recognition as sr
from output import say, engine
import json
import random
from functions import *
# from key import key
# import openai

# openai.api_key = key

def load_speech():
    with open("speech.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def speech_commands(text: str):
    data = load_speech()
    responses = []
    text = text.lower()
    for phrase in data:
        for input_words in phrase['input']:
            if input_words in text:
                output = random.choice(phrase['output'])
                function_name = phrase.get("function")
                if function_name:
                    func = globals().get(function_name)
                    if func:
                        output_func = func(text)
                        for key in output_func.keys():
                            output = output.replace(f'[{key}]', str(output_func[key]))
                responses.append(output)
                print(output)
    return responses

def main():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        say("Привет, я твой голосовой помощник, чем могу помочь?")
        
        while True:
            engine.runAndWait()
            print("ready")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = recognizer.recognize_google(audio, language='ru-RU')
                print(f"Вы сказали: {text}")
                responses = speech_commands(text)
                if responses:
                    for response in responses:
                        say(response)
                else:
                    variants = [
                        "Я тебя не понимаю",
                        "Простите, не могу разобрать",
                        "Повторите, пожалуйста."
                    ]
                    say(random.choice(variants))
                        
            except sr.UnknownValueError:
                print("Не удалось распознать звук")
            except sr.RequestError:
                print("request error")
            except sr.WaitTimeoutError:
                print("wait timeout, продолжаю ожидание...")

main()

