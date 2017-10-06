from time import ctime, sleep
import os
import requests
import speech_recognition as sr
from gtts import gTTS
import playsound
from bs4 import BeautifulSoup
import pymorphy2
import random

user_city = 'люблин'
r = sr.Recognizer()
file_names = []

def get_joke():
    url = 'http://anekdoty.ru/pro-robotov/'
    # url2 = 'http://anekdoty.ru/'
    r = requests.get(url)
    html = r.text
    result_tab = []
    soup = BeautifulSoup(html,'lxml')
    page = soup.find('ul',class_='item-list')
    jokes = page.find_all('li')
    
    for joke in jokes:
        result_tab.append(joke.p.text.strip())
    speak(random.choice(result_tab))


def remove_files():
    for file in file_names:
        os.remove(file)

def repeat():
    playsound.playsound(file_names[-1])

        
def wiki_parse(URL):
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'lxml')
    text = soup.find('div', class_='mw-parser-output').find_all('p')[:2]
    whole_text = ''
    for tab in text:
        whole_text += tab.text
    answer = ''
    sentence_count = 0
    for sentence in whole_text.split('.'):
        if(len(sentence) > 10):
            sentence_count += 1
        if(sentence_count == 3):
            break
        answer += sentence + '. '
    speak(answer)


def get_tommorow_weather(word = user_city):
    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse(word)[0]
    city = p.normal_form
    URL = 'https://sinoptik.ua/погода-'+city.lower().replace(' ','-')
    response = requests.get(URL)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    page = soup.find('div',class_="main",id = 'bd2')
    data = page.text.strip()
    description = page.find('div',class_='weatherIco')["title"]
    data = data.replace('мин.', 'минимальная температура')
    data = data.replace('макс.', '. Максимальная температура')
    speak('{}. {}'.format(data, description+'.'))
    os.system("start chrome https://sinoptik.ua/погода-%s"%city)


def speak(audioString):
    now = ctime().split()[-2].replace(':', '-')
    name = now + "audio.mp3"
    file_names.append(name)
    print(audioString)
    tts = gTTS(text=audioString, lang='ru')
    tts.save(name)
    playsound.playsound(name)
 

def recordAudio():
    with sr.Microphone() as source:
        print("Я тебя слушаю...")
        audio = r.listen(source)
    data = ""
    try:
        data = r.recognize_google(audio, language="ru_RU")
        print("Ты сказал... : " + data)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return data # string

 
def jarvis(data):
    # повторить последний текст
    if "выключись" in data or 'выключить' in data or 'пока' in data:
        speak("До встречи")
        remove_files()
        exit()

    if "как дела" in data:
        speak("Да отлично вообще. А у тебя?")
 
    if "который час" in data:
        time = '{} часов {} минут'.format(*ctime().split()[-2].split(':')[:2])
        speak(time)
 
    if "где находится" in data:
        data = data.split(" ")
        start = data.index('находится')
        location = ' '.join(data[start+1:])
        speak("Подожди секундочку, сейчас я покажу где находится "+location)
        os.system("start chrome https://www.google.nl/maps/place/%s"%location)

    # поиск по вики
    if "что такое" in data:
        data = data.split(" ")
        start = data.index('такое')
        search = ' '.join(data[start+1:])
        URL = "https://ru.wikipedia.org/wiki/%s"%search
        speak("Подожди секундочку, сейчас я расскажу что такое "+ search)
        os.system("start chrome https://ru.wikipedia.org/wiki/%s"%search)
        wiki_parse(URL)


    if "погода на завтра в" in data or 'завтра в' in data:
        data = data.split(" ")
        start = data.index('в')
        search = ' '.join(data[start+1:])
        get_tommorow_weather(search)

    if "погода на завтра" in data:
        get_tommorow_weather(user_city)

    # Шутки
    if 'пошути' in data or "расскажи анекдот" in data or 'расскажи шутку' in data:
        get_joke()


    if "повтори" in data:
        repeat()
    # Игра города голосом


 
def main():
    print('Минутку тишины, пожалуйста...')
    sleep(1)
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)

    speak("Привет, чем могу помочь?")
    while 1:
        data = recordAudio().lower()
        jarvis(data)

        
if __name__ == '__main__':
    main()
