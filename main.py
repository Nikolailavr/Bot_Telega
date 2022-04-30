import time
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import keyboard


class Stocks:
    print("\n Let's go! Begin work \n")
    url = 'https://www.google.com/finance/quote/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}
    rus_content_text = ["АФК Система", "Аэрофлот", "АЛРОСА", "МКБ", "Северсталь", "Детский мир", "En+ Group",
                        "ФСК ЕЭС", "X5 RetailGroup", "Fix Price", "Газпром", "Globaltrans", "Норникель",
                        "HeadHunter", "РусГидро", "Интер РАО ЕЭС", "Лукойл", "Магнитогорский метал", "Магнит",
                        "Московская биржа", "МТС", "НЛМК", "Новатэк", "Озон", "ПИК", "Полюс Золото",
                        "Petropavlovsk PLC",
                        "Polymetal", "Роснефть", "Ростелеком", "Русал", "Сбербанк", "Сургутнефтегаз",
                        "Татнефть", "TCS Group", "Транснефть", "VK", "Банк ВТБ",
                        "Яндекс"]
    rus_content_data = ["AFKS", "AFLT", "ALRS", "CBOM", "CHMF", "DSKY", "ENPG",
                        "FEES", "FIVE", "FIXP", "GAZP", "GLTR", "GMKN", "HHR",
                        "HYDR", "IRAO", "LKOH", "MAGN", "MGNT", "MOEX", "MTSS",
                        "NLMK", "NVTK", "OZON", "PIKK", "PLZL", "POGR", "POLY",
                        "ROSN", "RTKM", "RUAL", "SBER", "SNGS", "TATN", "TCSG",
                        "TRNFP", "VKCO", "VTBR", "YNDX"]

    index_content_text = ["S&P 500", "NASDAQ", "Dow Jones", "Russell 2000", "Индекс РТС",
                          "Индекс Московской биржи"]
    index_content_data = [".INX:INDEXSP", ".IXIC:INDEXNASDAQ", ".DJI:INDEXDJX",
                          "RUT:INDEXRUSSELL", "RTSI:MCX", "IMOEX:MCX"]

    def find_tiker(self, tiker):
        mess = ""
        exchange = ["", ":MCX", ":NASDAQ", ":NYSE"]
        flag = False
        for i in exchange:
            if self.check_url(tiker + i):
                if tiker in self.rus_content_data or tiker in self.index_content_data:
                    try:
                        text = self.rus_content_text[self.rus_content_data.index(tiker)]
                    except Exception:
                        text = self.index_content_text[self.index_content_data.index(tiker)]
                    mess = text + " (#" + tiker + "): <b> " + self.get_currency_price(tiker + i) + "</b>"
                else:
                    mess = tiker + ": <b> " + self.get_currency_price(tiker + i) + "</b>"
                flag = True
                break
        if not flag:
            mess = "<b>Неверный запрос: </b>" + tiker
        return mess

    def get_currency_price(self, tiker):
        full_page = requests.get(self.url + tiker, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll("div", {"class": "YMlKec fxKbKc"})
        #    return re.sub(r"\s+", "", convert[0].text, 0).replace(",", ".")
        return convert[0].text

    def check_url(self, tiker):
        full_page = requests.get(self.url + tiker, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll("div", {"class": "YMlKec fxKbKc"})
        if len(convert) > 0:
            return True
        else:
            return False

    def gen_markup(self, country, page):
        markup = types.InlineKeyboardMarkup(row_width=3)
        x = (page - 1) * 6
        text = self.rus_content_text
        data = self.rus_content_data
        match country:
            case 1:
                text = self.rus_content_text
                data = self.rus_content_data
            case 2:
                text = self.index_content_text
                data = self.index_content_data
        flag_end = x + 6 >= len(text)  # Flag that show end of array
        try:
            markup.add(types.InlineKeyboardButton(text[x], callback_data=data[x]),
                       types.InlineKeyboardButton(text[x + 1], callback_data=data[x + 1]),
                       types.InlineKeyboardButton(text[x + 2], callback_data=data[x + 2]))
            markup.add(types.InlineKeyboardButton(text[x + 3], callback_data=data[x + 3]),
                       types.InlineKeyboardButton(text[x + 4], callback_data=data[x + 4]),
                       types.InlineKeyboardButton(text[x + 5], callback_data=data[x + 5]))
        except Exception:
            pass
        finally:
            if flag_end and page == 1:
                markup.add(types.InlineKeyboardButton("Выход", callback_data="exit"))
            elif page == 1:
                markup.add(types.InlineKeyboardButton("Выход", callback_data="exit"),
                           types.InlineKeyboardButton("Дальше", callback_data=(page + 1)))
            elif flag_end:
                markup.add(types.InlineKeyboardButton("Назад", callback_data=(page - 1)),
                           types.InlineKeyboardButton("Выход", callback_data="exit"))
            else:
                markup.add(types.InlineKeyboardButton("Назад", callback_data=(page - 1)),
                           types.InlineKeyboardButton("Выход", callback_data="exit"),
                           types.InlineKeyboardButton("Дальше", callback_data=(page + 1)))
        return markup


bot = telebot.TeleBot('{API}', threaded=False)
stocks = Stocks()
stop = False

@bot.message_handler(commands=['start'])
def start(message):
    menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    menu.add(types.KeyboardButton("Акции Московской биржы"), types.KeyboardButton("Основные индексы"),
             types.KeyboardButton("Поблагодарить автора"))
    bot.send_message(message.chat.id,
                     f'Приветствую тебя <b>{message.from_user.first_name} {message.from_user.last_name}</b>',
                     parse_mode='html', reply_markup=menu)


@bot.message_handler(commands=['moex'])
def moex(message):
    bot.send_message(message.chat.id, "Акции Московской биржы", reply_markup=stocks.gen_markup(1, 1))


@bot.message_handler(commands=['index'])
def index(message):
    bot.send_message(message.chat.id, "Основные индексы", reply_markup=stocks.gen_markup(2, 1))


@bot.message_handler(commands=['pay', 'donat'])
def pay(message):
    link_pay = types.InlineKeyboardMarkup()
    link_pay.add(types.InlineKeyboardButton("Юmoney", url="{umoney}"),
                 types.InlineKeyboardButton("QIWI", url="{QIWI}"))
    bot.send_message(message.chat.id, "Карта: <b>{card_no}</b>", parse_mode='html',
                          reply_markup=link_pay)
    bot.send_message(message.chat.id, "Спасибо!", parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message.text == "Акции Московской биржы":
        country = 1
    else:
        country = 2
    if call.data.isnumeric():
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=stocks.gen_markup(country, int(call.data)))
    elif call.data == "exit":
        bot.delete_message(call.from_user.id, call.message.message_id)
    else:
        bot.send_message(call.from_user.id, stocks.find_tiker(call.data), parse_mode='html')


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    match message.text:
        case "Акции Московской биржы":
            moex(message)
        case "Основные индексы":
            index(message)
        case "Поблагодарить автора":
            pay(message)
        case _:
            bot.send_message(message.chat.id, stocks.find_tiker(message.text.upper()), parse_mode='html')


def break_bot():
    global stop
    print('finishing the loop')
    stop = True
    bot.stop_bot()


while not stop:
    keyboard.add_hotkey('ctrl+`', lambda: break_bot())
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        print("\n !!! ConnectionError !!!\n")
        print("---Try restart bot---")
        time.sleep(30)
