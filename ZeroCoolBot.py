# coding=utf-8
import pyowm
import telebot
import requests
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup as bs
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import bot_token, binance_api_key, binance_api_secret

owm = pyowm.OWM('caf14d0af187617f830a3e39dffa2de9', language='ru')
bot = telebot.TeleBot(bot_token)

headers = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'}

cbr_url = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req=' + str(datetime.today().strftime('%d/%m/%Y'))

# add filemode="w" to overwrite
logging.basicConfig(filename='ZeroCoolBot.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d %b %y %H:%M:%S', level=logging.INFO)


@bot.message_handler(commands=['help'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, '/rate или /курс - курс валюты \n/rates или /курсы - курс всех валют \n/crypto или /крипта - курс крипты \nИли введите название города и узнаете погоду')
    except Exception as e:
        logging.error("Exception occurred in start_message_help", exc_info=e)


# курс крипты
def binance():
    client = Client(binance_api_key, binance_api_secret)
    try:
        # prices = client.get_all_tickers()
        btc = client.get_margin_price_index(symbol='BTCUSDT')
        btc_cp = json.loads(json.dumps(client.get_ticker(symbol='BTCUSDT')))
        eth = client.get_margin_price_index(symbol='ETHUSDT')
        eth_cp = json.loads(json.dumps(client.get_ticker(symbol='ETHUSDT')))
        xrp = client.get_margin_price_index(symbol='XRPUSDT')
        xrp_cp = json.loads(json.dumps(client.get_ticker(symbol='XRPUSDT')))
        bch = client.get_margin_price_index(symbol='BCHABCUSDT')
        bch_cp = json.loads(json.dumps(client.get_ticker(symbol='BCHABCUSDT')))
        ltc = client.get_margin_price_index(symbol='LTCUSDT')
        ltc_cp = json.loads(json.dumps(client.get_ticker(symbol='LTCUSDT')))
        coin = 'Топ-5 криптовалют на ' + str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')) + '\n\n' + \
               'BTC - ' + str(round(float(btc['price']), 2)) + ' $ (' + str(
            round(float(btc_cp["priceChangePercent"]), 2)) + '%)' + '\n' + 'ETH - ' + str(round(float(eth['price']), 2)) + ' $ (' + str(
            round(float(eth_cp["priceChangePercent"]), 2)) + '%)' + '\n' + 'XRP - ' + str(round(float(xrp['price']), 3)) + ' $ (' + str(
            round(float(xrp_cp["priceChangePercent"]), 2)) + '%)' + '\n' + 'BCH - ' + str(round(float(bch['price']), 2)) + ' $ (' + str(
            round(float(bch_cp["priceChangePercent"]), 2)) + '%)' + '\n' + 'LTC - ' + str(round(float(ltc['price']), 2)) + ' $ (' + str(
            round(float(ltc_cp["priceChangePercent"]), 2)) + '%)'
        # time.strftime('%d.%m.%Y %H:%M:%S', time.gmtime(btc['calcTime']/1000.))
        return coin
    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)
        logging.error("Exception occurred in binance", exc_info=True)


# binance()


@bot.message_handler(commands=['coin', 'crypto', 'крипта'])
def send_welcome(message):
    try:
        answer = binance()
        print(str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')) + ' Запрос курса крипты')
        logging.info('Запрос курса крипты')
        bot.send_message(message.chat.id, str(answer))
    except Exception as e:
        logging.error('Exception occurred in send_welcome_coin', exc_info=e)


# курс 3х валют
def cbr_parse():
    try:
        session = requests.Session()  # видимость того что один пользователь просмтривает много инфы
        request = session.get(cbr_url, headers=headers)  # эмуляция открыия страницы в браузере
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
            nominals = soup.find_all('nominal')
            names = soup.find_all('name')
            values = soup.find_all('value')
            rate = 'Курс ЦБ России на ' + str(datetime.today().strftime('%d.%m.%Y')) + '\n\n'
            rate += nominals[10].get_text() + ' ' + names[10].get_text() + ' - ' + str(round(float(values[10].get_text().replace(',', '.', 1)), 2)) + ' ₽' + '\n'
            rate += nominals[11].get_text() + ' ' + names[11].get_text() + ' - ' + str(round(float(values[11].get_text().replace(',', '.', 1)), 2)) + ' ₽' + '\n'
            rate += nominals[27].get_text() + ' ' + names[27].get_text() + ' - ' + str(round(float(values[27].get_text().replace(',', '.', 1)), 2)) + ' ₽'
            return rate
        else:
            print('error_cbr_parse')
    except Exception as e:
        logging.error("Exception occurred in cbr_parse", exc_info=e)


@bot.message_handler(commands=['rate', 'курс'])
def send_welcome(message):
    try:
        answer = cbr_parse()
        print(str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')) + ' Запрос курса валют')
        logging.info('Запрос курса валют')
        bot.send_message(message.chat.id, str(answer))
    except Exception as e:
        logging.error('Exception occurred in send_welcome_rate', exc_info=e)


# курс всех валют
def cbr_parse_all():
    try:
        session = requests.Session()  # видимость того что один пользователь просмтривает много инфы
        request = session.get(cbr_url, headers=headers)  # эмуляция открыия страницы в браузере
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')  # получаем весь контент, заменяем html.parser на lxml
            nominals = soup.find_all('nominal')
            names = soup.find_all('name')
            values = soup.find_all('value')
            # soup.find('div', {'class': 'test'})
            # print('Сегодня ' + str(datetime.today().strftime('%d.%m.%Y')) + ', кол-во валют - ' + str(len(names)))
            # rate = 'Сегодня ' + str(datetime.today().strftime('%d.%m.%Y')) + ', кол-во валют - ' + str(len(names)) + '\n'
            rate = 'Курс ЦБ России на ' + str(datetime.today().strftime('%d.%m.%Y')) + '\n\n'
            for i in range(0, len(names)):
                rate += nominals[i].get_text() + ' ' + names[i].get_text() + ' - ' + str(round(float(values[i].get_text().replace(',', '.', 1)), 2)) + ' ₽' + '\n'
            return rate
        else:
            print('error_cbr_parse_all')
    except Exception as e:
        logging.error('Exception occurred in cbr_parse_all', exc_info=e)


@bot.message_handler(commands=['rates', 'курсы'])
def send_welcome(message):
    try:
        answer = cbr_parse_all()
        # print(answer)
        print(str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')) + ' Запрос всех курсов валют')
        logging.info('Запрос всех курсов валют')
        bot.send_message(message.chat.id, str(answer))
    except Exception as e:
        logging.error('Exception occurred in send_welcome_rates', exc_info=e)


# погода в городах
@bot.message_handler(content_types=['text'])
def send_echo(message):
    try:
        observation = owm.weather_at_place(message.text)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')['temp']
        wind = w.get_wind()['speed']
        humidity = w.get_humidity()
        answer = 'В городе ' + message.text + ' сейчас ' + w.get_detailed_status() + ', температра ' + str(
            temp) + '°, скорость ветра ' + str(wind) + 'м/с, влажность ' + str(humidity) + '%. '
        if temp < 10:
            answer += 'Сейчас холодно, одевайтесь тепло.'
        elif temp < 20:
            answer += 'Сейчас прохладно, одевайтесь теплее.'
        else:
            answer += 'Температура ok, одевайтесь легко.'
        if w.get_detailed_status() == 'небольшой дождь' \
                or w.get_detailed_status() == 'дождь' \
                or w.get_detailed_status() == 'гроза':
            answer += ' Не забудьте взять зонт.'
        bot.send_message(message.chat.id, answer)
        print(str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')) + ' Запрос погоды для города ' + message.text)
        logging.info('Запрос погоды для города ' + message.text)
    except Exception as e:
        logging.error('Exception occurred in send_echo_town', exc_info=e)
        answer = 'Город не найден, попробуйте ввести на английском языке'
        bot.send_message(message.chat.id, answer)


logging.info('Запущен ZeroCoolBot')
print('ZeroCoolBot запущен ' + str(datetime.today().strftime('%d.%m.%Y %H:%M:%S')))

bot.polling(none_stop=True)  # бесконечный бот
