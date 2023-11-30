import time

import cherrypy
import threading
import telebot
from telebot import types as tp
from telebot import apihelper

import config as cfg
import penalti as pnt
import payment as pt
import admin as adm
import lucky_strike as ls
import timers as tm

# вот тут ваш ip адрес сервера
WEBHOOK_HOST = ''
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % cfg.token

# Имя канала для проверки на подписку
CHANNEL_ID = ""

bot = telebot.TeleBot(cfg.token)
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


# изменил эту функцию
def is_subscribed(USER_ID):
    try:
        result = str(bot.get_chat_member(CHANNEL_ID, USER_ID))
        if 'left' not in result:
            return True
        else:
            return False
    except apihelper.ApiException as error:
        print(error)
        return True


# эта функция тоже была переписана
def search_user_by_username(user_name, tele_id):
    username = user_name.replace("@", "")
    user_list = cfg.select_all_users()
    for user in user_list:
        if username == bot.get_chat_member(CHANNEL_ID, user[0]).user.username and user[0] != tele_id:
            return user[0]
    return -1


# здесь тоже изменение
def get_username_by_id(tele_id):
    user = bot.get_chat_member(CHANNEL_ID, tele_id)
    username = user.user.username
    return str(username)


# функция завершения игры в самом боте для упрощения синтаксиса
def check_finish_game_penalti(call: tp.CallbackQuery, res: list, scores: list):
    finished = pnt.is_finished(call.message.chat.id)
    # обработка ошибок
    if finished == -1:
        old_markup = tp.InlineKeyboardMarkup()
        old_markup.add(tp.InlineKeyboardButton(
            text="🧑💻 В личный кабинет", callback_data="back"))
        error_str = "Во время игры возникла ошибка, сеанс бы завершен"
        msg = bot.send_message(chat_id=call.message.chat.id,
                               text=error_str, reply_markup=old_markup)
        cfg.insert_lk_message_id(msg.message_id, msg.chat.id)
        msg = bot.send_message(chat_id=pnt.get_second_user(
            call.message.chat.id), text=error_str, reply_markup=old_markup)
        cfg.insert_lk_message_id(msg.message_id, msg.chat.id)
        pnt.delete_game(call.message.chat.id)
        return True
    # обработка успешного завершения игры
    if finished:
        game_res = pnt.finish_game(call.message.chat.id)
        if game_res[0] == 0:
            markup = tp.InlineKeyboardMarkup()
            markup.add(tp.InlineKeyboardButton(
                text="⚽️ Переигровка", callback_data="penalti"))
            markup.add(tp.InlineKeyboardButton(
                text="🏳️ Ничья", callback_data="new_lk"))
            draw_str = f"Результаты ударов @{get_username_by_id(res[1])}:\n{scores[0]}\n" \
                       f"Результаты ударов @{get_username_by_id(res[2])}:\n{scores[1]}\n" \
                       f"🏆 Вы забили одинаковое количество голов! " \
                       f"Предлагаем вам переигровку или же ничью, выбор за вами!"
            msg = bot.send_message(res[1], text=draw_str, reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, game_res[1])
            msg = bot.send_message(res[2], text=draw_str, reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, game_res[2])
        else:
            markup = tp.InlineKeyboardMarkup()
            markup.add(tp.InlineKeyboardButton(
                text="🧑💻 В личный кабинет", callback_data="back"))
            markup.add(tp.InlineKeyboardButton(
                text="⚽️ Рейтинг игроков в Пенальти", callback_data="rate_pen"))
            fin_str = f"Результаты ударов @{get_username_by_id(res[1])}:\n{scores[0]}\n" \
                      f"Результаты ударов @{get_username_by_id(res[2])}:\n{scores[1]}\n" \
                      f"Победитель - @{get_username_by_id(game_res[1])}"
            msg = bot.send_message(
                game_res[1], text=fin_str, reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, game_res[1])
            msg = bot.send_message(
                game_res[2], text=fin_str, reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, game_res[2])
        pnt.delete_game(call.message.chat.id)
        return True
    return False


# переписана эта функция (destroy_penalti_game раньше)
def time_events_checker():
    while True:
        games_list = pnt.select_all_games()
        if games_list is not None:
            for game in games_list:
                result = pnt.destroy_game(game[0])
                if result[0] != 0:
                    markup = tp.InlineKeyboardMarkup()
                    markup.add(tp.InlineKeyboardButton(
                        text="🧑💻 В личный кабинет", callback_data="back"))
                    if result[2]:
                        markup.add(tp.InlineKeyboardButton(
                            text="⚽️ Рейтинг игроков в Пенальти", callback_data="rate_pen"))
                        msg = bot.send_message(result[0],
                                               "Игрок - @" + get_username_by_id(
                                                   result[1]) + " слишком долго не отвечал, вы победили!",
                                               reply_markup=markup)
                        cfg.insert_lk_message_id(msg.message_id, result[0])
                        msg = bot.send_message(result[1],
                                               "Тебя слишком долго не было в игре, поэтому тебе засчитано поражение",
                                               reply_markup=markup)
                        cfg.insert_lk_message_id(msg.message_id, result[1])
                    else:
                        msg = bot.send_message(result[0],
                                               "Матч признан несостоявшимся из-за длительного ожидания 🏳️",
                                               reply_markup=markup)
                        cfg.insert_lk_message_id(msg.message_id, result[0])
                        msg = bot.send_message(result[1],
                                               "Матч признан несостоявшимся из-за длительного ожидания 🏳️",
                                               reply_markup=markup)
                        cfg.insert_lk_message_id(msg.message_id, result[1])
        time.sleep(10)
        # проверка юзеров на возможность получить карточку
        user_list = cfg.get_users_id_for_free_card()
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🃏 Получить карту", callback_data="0"))
        markup.add(tp.InlineKeyboardButton(
            text="🧑💻 В личный кабинет", callback_data="back"))
        for user_id in user_list:
            if is_subscribed(user_id):
                try:
                    msg = bot.send_message(user_id, "Привет! Ты можешь забрать свою бесплатную карту! 🎁",
                                           reply_markup=markup)
                    cfg.insert_lk_message_id(msg.message_id, user_id)
                    cfg.set_get_msg(user_id, 1)
                except apihelper.ApiException as e:
                    print(e)
        tm.unban_users()
        ls.give_free_strikes()
        time.sleep(30)


# получение нового сообщения с личным кабинетом
def go_to_lk_message(CHAT_ID):
    user = cfg.search_user_in_db(CHAT_ID)
    cfg.calc_card_rating(CHAT_ID)
    cfg.cancel_trade(CHAT_ID)
    markup = tp.InlineKeyboardMarkup()
    # первый ряд кнопок (просмотр коллекции, получить карту)
    coll_btn = tp.InlineKeyboardButton(
        text="🧳 Моя коллекция", callback_data="one_by_0")
    card_btn = tp.InlineKeyboardButton(
        text="🃏 Получить карту", callback_data="getcar")
    markup.row(card_btn, coll_btn)
    # второй ряд кнопок
    change_btn = tp.InlineKeyboardButton(
        text="🎭 Обмен картами", callback_data="chan_by_0")
    rate_btn = tp.InlineKeyboardButton(
        text="🏆 Общий рейтинг", callback_data="rate")
    markup.row(change_btn, rate_btn)
    # ряд с мини-игрой
    markup.row(tp.InlineKeyboardButton(
        text="🎲 Мини-игры", callback_data="games"))
    if cfg.is_admin(CHAT_ID):
        markup.row(tp.InlineKeyboardButton(
            text="Админская панель", callback_data="admin"))
    # ряд с кнопкой назад
    markup.row(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="menu"))
    # строчка со статистикой для игрока
    stat_str = "Твои достижения:\n\n🃏 Собранное количество карточек: " + str(user[1]) + "\n" \
                                                                                        "🏆 Рейтинг собранных карточек:" + str(
        user[2]) + "\n\n" \
                   "⚽️ Рейтинг в игре Пенальти: " + str(user[3])
    msg = bot.send_message(chat_id=CHAT_ID, text=stat_str, reply_markup=markup)
    cfg.insert_lk_message_id(msg.message_id, CHAT_ID)


# стартовое сообщение
@bot.message_handler(commands=['start'])
def start_message(message):
    cfg.clear_non_active_users()
    # изменена проверка ниже
    if not is_subscribed(message.from_user.id):
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Подписаться \U00002705", url="https://t.me/offsidecard"))
        bot.send_message(message.from_user.id,
                         "Чтобы начать играть, необходимо:\n"
                         "1️⃣ Подписаться на канал @offsidecard\n"
                         "2️⃣ Нажать на /start",
                         reply_markup=markup)
    elif not tm.check_spam(message.from_user.id):
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="ℹ️ Информация", callback_data="info"))
        markup.add(tp.InlineKeyboardButton(
            text="🎮 Начать игру", callback_data="back"))
        cfg.place_user_in_bd(message.from_user.id)
        msg = bot.send_message(message.from_user.id,
                               "👋 *Добро пожаловать в OFFSide*\n\n"
                               "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                               "из медиафутбола и играть в мини-игры.\n\n"
                               "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                               "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                               "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                               "Все правила игры вы можете узнать в разделе: *«ℹ️ Информация»*\n\n"
                               "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                               reply_markup=markup, parse_mode='Markdown')
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)


# получение сообщение меню
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def back_to_menu(call):
    cfg.clear_non_active_users()
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="ℹ️ Информация", callback_data="info"))
    markup.add(tp.InlineKeyboardButton(
        text="🎮 Начать игру", callback_data="back"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="👋 *Добро пожаловать в OFFSide*\n\n"
                               "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                               "из медиафутбола и играть в мини-игры.\n\n"
                               "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                               "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                               "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                               "Все правила игры вы можете узнать в разделе: *«ℹ️ Информация»*\n\n"
                               "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                          reply_markup=markup, parse_mode='Markdown')


# сообщение с информацией
@bot.callback_query_handler(func=lambda call: call.data == "info")
def answer_info_callback(call):
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="🃏 О картах", callback_data="card_info"))
    markup.add(tp.InlineKeyboardButton(
        text="⚽️ О пенальти", callback_data="penalti_info"))
    markup.add(tp.InlineKeyboardButton(
        text="☘️ Об удачном ударе", callback_data="strike_info"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="menu"))
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    bot.edit_message_text(message_id=msg_id, chat_id=call.message.chat.id,
                          text="В этом разделе можно найти информацию про наш проект", reply_markup=markup)


# сообщение с получением более подробной информации
@bot.callback_query_handler(func=lambda call: "_info" in call.data)
def answer_questions(call):
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="menu"))
    if call.data == "card_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id,
                              text="Каждая карта имеет свою редкость и количество баллов, которые она добавляет к твоему рейтингу:\n\n"
                                   "1) Легендарная редкость: Карта добавляет 1000 баллов к твоей коллекции.\n\n"
                                   "2) Уникальная редкость: Карта добавляет 500 баллов к твоей коллекции.\n\n"
                                   "3) Эпическая редкость: Карта добавляет 250 баллов к твоей коллекции.\n\n"
                                   "4) Необычная редкость: Карта добавляет 100 баллов к твоей коллекции.\n\n"
                                   "5) Обычная редкость: Карта добавляет 50 баллов к твоей коллекции.\n\n",
                              reply_markup=markup)
    if call.data == "penalti_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id,
                              text="Игра в пенальти, это отдельный режим в OFFSIDE, "
                                   "в которой тебе нужно забивать и отбивать мячи.\n\n"
                                   "Чтобы начать игру в пенальти, вам нужно:\n"
                                   "1. Зайти в раздел  «🎲 Мини-игры»\n"
                                   "2. Выбрать игру «⚽️ Пенальти»\n"
                                   "3. Отправить приглашение пользователю с которым вы хотите сыграть.\n"
                                   "Игрок пригласивший второго пользователя будет первым делать удары. "
                                   "Второй игрок будет начинать в роли вратаря, его задача: стараться выбрать верную цифру,"
                                   " чтобы прыгнуть в определенный угол и отразить удар. "
                                   "Далее вы меняетесь местами, такой процесс повторяется пять раз для каждого игрока. "
                                   "В итоге, выигрывает тот игрок, который забил больше всего мячей. "
                                   "В результате игры возможна ничья.\n\n"
                                   "За каждую победу игроку начисляется  +25 баллов, а за поражение снимается -25 баллов. "
                                   "Всем игрокам дается изначальный рейтинг 100. "
                                   "За согласование ничьей рейтинг у обоих игроков не изменяется.",
                              reply_markup=markup)
    if call.data == "strike_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id,
                              text="Чтобы начать игру в удачный удар, вам нужно:\n"
                                   "1. Зайти в раздел  «🎲 Мини-игры»\n"
                                   "2. Выбрать игру «☘️ Удачный удар»\n"
                                   "3. Нажать на кнопку «⚽️ Сделать удар»\n\n"
                                   "☘️ Удачный удар - это мини-игра, в которой ты делаешь 1 удар по воротам.\n"
                                   "Если забиваешь - получаешь одну рандомную карточку.\n"
                                   "Если не забиваешь - пробуешь еще через 4 часа.\n"
                                   "В день доступно 2 бесплатные попытки.\n"
                                   "Если тебе сегодня везет и хочешь сделать больше ударов по воротам - "
                                   "можешь приобрести дополнительные попытки.",
                              reply_markup=markup)


# обработка callback'a для личного кабинета
@bot.callback_query_handler(func=lambda call: call.data == "back")
def return_to_lk(call):
    user = cfg.search_user_in_db(call.message.chat.id)
    cfg.calc_card_rating(call.message.chat.id)
    cfg.cancel_trade(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    # первый ряд кнопок (просмотр коллекции, получить карту)
    coll_btn = tp.InlineKeyboardButton(
        text="🧳 Моя коллекция", callback_data="one_by_0")
    card_btn = tp.InlineKeyboardButton(
        text="🃏 Получить карту", callback_data="getcar")
    markup.row(card_btn, coll_btn)
    # второй ряд кнопок
    change_btn = tp.InlineKeyboardButton(
        text="🎭 Обмен картами", callback_data="chan_by_0")
    rate_btn = tp.InlineKeyboardButton(
        text="🏆 Общий рейтинг", callback_data="rate")
    markup.row(change_btn, rate_btn)
    # ряд с мини-игрой
    markup.row(tp.InlineKeyboardButton(
        text="🎲 Мини-игры", callback_data="games"))
    if cfg.is_admin(call.message.chat.id):
        markup.row(tp.InlineKeyboardButton(
            text="Админская панель", callback_data="admin"))
    # ряд с кнопкой назад
    markup.row(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="menu"))
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    # строчка со статистикой для игрока
    stat_str = "Твои достижения:\n\n🃏 Собранное количество карточек: " + str(user[1]) + "\n" \
                                                                                        "🏆 Рейтинг собранных карточек:" + str(
        user[2]) + "\n\n" \
                   "⚽️ Рейтинг в игре Пенальти: " + str(user[3])
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=msg_id, text=stat_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "rate")
def get_player_rating(call):
    cfg.calc_card_rating(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="🃏 Рейтинг коллекционеров карточек", callback_data="rate_card"))
    markup.add(tp.InlineKeyboardButton(
        text="⚽️ Рейтинг игроков в Пенальти", callback_data="rate_pen"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="В этом разделе ты можешь посмотреть 🏆Топ 10 игроков по категориям!",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "rate_" in call.data)
def get_top_places(call):
    num = 1
    ans_str = ""
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    places = cfg.get_user_places(call.message.chat.id)
    if call.data == "rate_card":
        card_top = cfg.get_top_places()[0]
        for user in card_top:
            ans_str += str(num) + ". @" + get_username_by_id(user[0]) \
                + " - " + str(user[2]) + "\n"
            num += 1
        if not cfg.user_in_top_ten(call.message.chat.id)[0]:
            user = cfg.search_user_in_db(call.message.chat.id)
            ans_str += "\n" + str(places[0]) + ". @" \
                       + get_username_by_id(call.message.chat.id) + \
                " - " + str(user[2])
    if call.data == "rate_pen":
        penalti_top = cfg.get_top_places()[1]
        for user in penalti_top:
            ans_str += str(num) + ". @" + get_username_by_id(user[0]) \
                + " - " + str(user[3]) + "\n"
            num += 1
        if not cfg.user_in_top_ten(call.message.chat.id)[1]:
            user = cfg.search_user_in_db(call.message.chat.id)
            ans_str += "\n" + str(places[1]) + ". @" \
                       + get_username_by_id(call.message.chat.id) + \
                " - " + str(user[3])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=ans_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "coll")
def get_collection(call):
    user_cards = cfg.get_user_card_list(call.message.chat.id)
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    if user_cards is None:
        markup.add(tp.InlineKeyboardButton(
            text="🃏 Получить карту", callback_data="getcar"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id,
                              text="Пока что ваша коллекция пуста", reply_markup=markup)
    else:
        markup.add(tp.InlineKeyboardButton(
            text="🃏 Получить карту", callback_data="getcar"))
        markup.add(tp.InlineKeyboardButton(
            text="\U0001F4F2 Начать просмотр по карточкам", callback_data="one_by_0"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        ans_str = "Список всех ваших карт: \n\n"
        num = 1
        cfg.calc_card_rating(call.message.chat.id)
        for i in range(0, len(user_cards[0])):
            ans_str += str(num) + ". " + str(user_cards[0][i][2]) + " (" + str(user_cards[0][i][3]) + ") - " + \
                str(user_cards[1][i].num) + " шт.\n"
            num += 1
        msg = bot.send_message(chat_id=call.message.chat.id,
                               text=ans_str, reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)


# вызов мини-игр
@bot.callback_query_handler(func=lambda call: call.data == "games")
def get_mini_games(call):
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="⚽️ Пенальти", callback_data="penalti"))
    markup.add(tp.InlineKeyboardButton(
        text="☘️ Удачный удар", callback_data="lucky_strike"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text="Тут находятся мини-игры, в которые можешь поиграть с друзьями и выяснить, кто из вас лучший🥇",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "penalti")
def penalti_message(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    if not pnt.user_in_game(call.message.from_user.id):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="✉️ Напишите @username пользователя, которому хотите предложить игру в Пенальти",
                              reply_markup=markup)
        bot.register_next_step_handler(call.message, get_username_for_pen)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы уже состоите в игре, закончите ее, чтобы начать следующую",
                              reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "lucky_strike")
def lucky_strike(call):
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="⚽️ Сделать удар", callback_data="do_strike"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="games"))
    msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text="☘️ Удачный удар - это мини-игра, в которой ты делаешь 1 удар по воротам. "
                                     "Если забиваешь - получаешь одну рандомную карточку.Если не забиваешь - "
                                     "пробуешь еще через время",
                                reply_markup=markup)
    cfg.insert_lk_message_id(msg.message_id, call.from_user.id)


# функция игры удачный удар
@bot.callback_query_handler(func=lambda call: call.data == "do_strike")
def do_strike(call):
    markup = tp.InlineKeyboardMarkup()
    free_info = ls.check_free_strike(call.from_user.id)
    purchased = ls.check_purchased_strikes(call.from_user.id)
    if free_info[0] or purchased[0]:
        msg = bot.send_dice(call.from_user.id, '⚽️')
        if msg.dice.value < 3:
            ls.update_user_strikes(call.from_user.id, -1)
            if not purchased[0] or purchased[1] == 1:
                msg_text = "☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           "Попробуй еще раз через 4 часа или получи 3 удара за 100 рублей!"
                markup.add(tp.InlineKeyboardButton(
                    text="💵 Купить 3 удара", callback_data="4"))
            else:
                msg_text = f"☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           f"У тебя осталось еще несколько попыток - {purchased[1] - 1}"
                markup.add(tp.InlineKeyboardButton(
                    text="⚽️ Сделать удар", callback_data="do_strike"))
            markup.add(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="games"))
        else:
            ls.update_user_strikes(call.from_user.id, -1)
            cfg.add_cards_to_user(ls.get_random_card(1), call.message.chat.id)
            msg_text = "☘️ Ты испытал удачу и выиграл одну случайную карточку!"
            markup.add(tp.InlineKeyboardButton(
                text="🃏 Получить карту", callback_data="get_new_cards"))
        msg = bot.send_message(
            call.from_user.id, msg_text, reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, call.from_user.id)
    elif not purchased[0]:
        msg_text = f"Ты недавно пробовал проверить свою удачу!\n" \
                   f"Приходи через {free_info[1].split(':')[0]}ч {free_info[1].split(':')[1]}мин" \
                   f" ⏱ или получи 3 удара за 100 рублей!"
        markup.add(tp.InlineKeyboardButton(
            text="💵 Купить 3 удара", callback_data="4"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="games"))
        bot.edit_message_text(text=msg_text, chat_id=call.from_user.id,
                              message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "cont_off")
def continue_offer(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id,
                          text="Введите юзернейм пользователя, с которым хотите поменяться")
    bot.register_next_step_handler(call.message, get_offer_to_user)


# получение карточек и их покупка (тоже исправлена и переписана)
@bot.callback_query_handler(func=lambda call: call.data == "getcar")
def get_cards(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    product_str = "🃏 Если ты хочешь получить карточку, то ты попал куда надо!\n\n" \
                  "Раз в 24 часа ты можешь получать одну карточку бесплатно, " \
                  "но если ты хочешь продвигаться по таблице рейтинга быстрее других" \
                  " и пополнять свою коллекцию, то рекомендуем тебе посетить магазин карт 🛍"
    markup.add(tp.InlineKeyboardButton(
        text="🎁 Получить бесплатную карточку", callback_data="0"))
    markup.add(tp.InlineKeyboardButton(
        text="🛍 Магазин карточек", callback_data="store"))
    markup.add(tp.InlineKeyboardButton(
        text="🧑‍💻 Ввести промокод", callback_data="input"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text=product_str, reply_markup=markup)


# новый хендлер для перехода в магазин карточек
@bot.callback_query_handler(func=lambda call: call.data == "store")
def get_card_shop(call):
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="💵 Купить одну рандомную карточку", callback_data="1"))
    markup.add(tp.InlineKeyboardButton(
        text="💵 Купить три рандомных карточки", callback_data="2"))
    markup.add(tp.InlineKeyboardButton(
        text="💵 Купить пять рандомных карточек", callback_data="3"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="getcar"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="🛍 Ты находишься в магазине карт, у нас есть несколько товаров:\n\n"
                               "💰 Одна рандомная карточка - 65 рублей\n"
                               "💰 Три рандомных карточки - 125 рублей\n"
                               "💰 Пять рандомных карточек - 185 рублей",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "input")
def wait_promo(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="getcar"))
    bot.edit_message_text("Введите промокод ниже",
                          call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, check_promocode)


# просмотр карточек одна за одной (хендлер частично переписан, вставьте заново) // был упрощен и оптимизирован код
# к сожалению было проблематично отметить какие-то новые строки, так как некоторые были удалены
# поэтому я указываю целую функцию, но я убрал из нее aka
@bot.callback_query_handler(func=lambda call: call.data.split("_")[0] == "one" or call.data.split("_")[0] == "chan")
def show_card_one_by_one(call):
    card_list = cfg.search_user_cards(call.message.chat.id)
    if card_list is None:
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🃏 Получить карту", callback_data="getcar"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        bot.edit_message_text(text="Ваша коллекция карточек сейчас пуста", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
        return
    if call.data.split("_")[0] != "chan":
        num = int(call.data.replace("one_by_", ""))
    else:
        num = int(call.data.replace("chan_by_", ""))
    card_num = cfg.search_user_in_db(call.message.chat.id)[1]
    markup = tp.InlineKeyboardMarkup()
    if call.data.split("_")[0] != "chan":
        list_btn = tp.InlineKeyboardButton(
            text="Просмотреть списком", callback_data="coll")
        next_btn = tp.InlineKeyboardButton(
            text=">>", callback_data="one_by_" + str(num + 1))
        back_btn = tp.InlineKeyboardButton(
            text="<<", callback_data="one_by_" + str(num - 1))
    else:
        markup.row(tp.InlineKeyboardButton(text="Выбрать для обмена",
                   callback_data="offer_" + str(card_list[num][0])))
        next_btn = tp.InlineKeyboardButton(
            text=">>", callback_data="chan_by_" + str(num + 1))
        back_btn = tp.InlineKeyboardButton(
            text="<<", callback_data="chan_by_" + str(num - 1))
    num_btn = tp.InlineKeyboardButton(
        text='(' + str(num + 1) + '/' + str(card_num) + ')', callback_data="...")
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    rareness = cfg.get_rareness_by_num(card_list[num][5])
    caption_str = str(card_list[num][2]) + " *" + str(card_list[num][3]) \
        + "*\nРейтинг: " + "*" + str(card_list[num][6]) \
        + "*\nКоманда: " + "*" + str(card_list[num][4]) + "*\n" \
        + "Редкость: " + "*" + rareness + "*"
    if len(card_list) == 1:
        markup.row(num_btn)
        if call.data.split("_")[0] != "chan":
            markup.row(list_btn)
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="new_lk"))
        else:
            markup.row(tp.InlineKeyboardButton(
                text="❌ Отклонить обмен", callback_data="trade_canc"))

        if call.message.photo is None:
            msg = bot.send_photo(call.message.chat.id, card_list[num][1], reply_markup=markup,
                                 caption=caption_str, parse_mode='Markdown')
            cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
            return
    if num == 0:
        markup.row(num_btn, next_btn)
        if call.data.split("_")[0] != "chan":
            markup.row(list_btn)
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="new_lk"))
        else:
            markup.row(tp.InlineKeyboardButton(
                text="❌ Отклонить обмен", callback_data="trade_canc"))

        if call.message.photo is None:
            msg = bot.send_photo(call.message.chat.id, card_list[num][1], reply_markup=markup,
                                 caption=caption_str, parse_mode='Markdown')
            cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
            return
    elif num == len(card_list) - 1:
        markup.row(back_btn, num_btn)
        if call.data.split("_")[0] != "chan":
            markup.row(list_btn)
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="new_lk"))
        else:
            markup.row(tp.InlineKeyboardButton(
                text="❌ Отклонить обмен", callback_data="trade_canc"))
    else:
        markup.row(back_btn, num_btn, next_btn)
        if call.data.split("_")[0] != "chan":
            markup.row(list_btn)
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="new_lk"))
        else:
            markup.row(tp.InlineKeyboardButton(
                text="❌ Отклонить обмен", callback_data="trade_canc"))
    bot.edit_message_media(chat_id=call.message.chat.id, message_id=msg_id,
                           media=tp.InputMediaPhoto(card_list[num][1]), reply_markup=markup)
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=msg_id,
                             caption=caption_str, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: "offer_" in call.data)
def insert_card_to_offer(call):
    # получаем id карточки, которую надо добавить из тела запроса
    card_id = int(call.data.replace("offer_", ""))
    # проверка на то, есть ли у второго юзера карточка, добавленная в обмен
    bool_pl = cfg.second_user_had_card(call.message.chat.id)
    # если обмен не определен (не существует у данного пользователя), то мы его создаем
    if not cfg.is_offer_defined(call.message.chat.id):
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        cfg.create_new_change_offer(call.message.chat.id, card_id)
        bot.send_message(call.message.chat.id,
                         "Напишите юзернейм пользователя (@username), с которым хотите обменяться")
        bot.register_next_step_handler(call.message, get_second_user_for_offer)
        return
    elif bool_pl != -1 and not bool_pl:
        cfg.add_card_to_offer(call.message.chat.id, card_id)
        msg = bot.send_message(
            call.message.chat.id, "✅ Предложение обмена успешно отправлено, ожидайте")
        cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
        user_id = cfg.get_first_user(call.message.chat.id)
        card = cfg.get_trade_card(user_id, 1)
        card1 = cfg.get_trade_card(user_id, 0)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="✅ Принять", callback_data="trade"))
        markup.add(tp.InlineKeyboardButton(
            text="❌ Отклонить обмен", callback_data="trade_canc"))
        bot.send_photo(chat_id=user_id, photo=card[1],
                       caption="✅ Пользователь ответил на ваше предложение обмена!\n"
                               "Вы получите эту карточку за вашу:\n" + card1[2] + " aka " + card1[3] + "\n" +
                               "С редкостью - " + cfg.get_rareness_by_num(card1[5]), reply_markup=markup)


# функция игры в пенальти
@bot.callback_query_handler(func=lambda call: "pen_" in call.data)
def penalti_game(call):
    if call.data == "pen_canc":
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🧑💻 В личный кабинет", callback_data="back"))
        res = pnt.delete_game(call.message.chat.id)
        msg = bot.send_message(call.message.chat.id, "❌ Вы отклонили игру в пенальти",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
        msg = bot.send_message(chat_id=res[0],
                               text=f"❌ @{get_username_by_id(res[1])} отклонил предложение игры",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, res[0])
        return
    if call.data == "pen_start":
        markup = tp.InlineKeyboardMarkup()
        btn_one = tp.InlineKeyboardButton(text="1️⃣", callback_data="pen_1")
        btn_two = tp.InlineKeyboardButton(text="2️⃣", callback_data="pen_2")
        btn_three = tp.InlineKeyboardButton(text="3️⃣", callback_data="pen_3")
        markup.row(btn_one, btn_two, btn_three)
        pnt.start_game(call.message.chat.id)
        kicker_id = pnt.get_kicker(call.message.chat.id)
        bot.send_photo(chat_id=call.message.chat.id, photo=open('images/keeper.png', 'rb'),
                       caption="Выбери сторону куда ты хочешь прыгнуть",
                       reply_markup=markup)
        bot.send_photo(chat_id=kicker_id, photo=open('images/keeper.png', 'rb'),
                       caption="Выбери угол, в который хочешь ударить",
                       reply_markup=markup)
    else:
        markup = tp.InlineKeyboardMarkup()
        btn_one = tp.InlineKeyboardButton(text="1️⃣", callback_data="pen_1")
        btn_two = tp.InlineKeyboardButton(text="2️⃣", callback_data="pen_2")
        btn_three = tp.InlineKeyboardButton(text="3️⃣", callback_data="pen_3")
        markup.row(btn_one, btn_two, btn_three)
        pnt.set_kick_time(call.message.chat.id)
        num = int(call.data.replace("pen_", ""))
        pnt.place_turn_in_db(call.message.chat.id, num)
        res = pnt.is_scored(call.message.chat.id)
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=f"Ваш выбор - {num}\nОжидайте хода второго игрока",
                                 reply_markup=None)
        scores = pnt.get_score_str(call.message.chat.id)
        if res[0]:
            kicker_text = f"⚽️ ГОЛ!!!\n@{get_username_by_id(res[2])} прыгнул в другую сторону\n" \
                          f"Результаты твоих ударов:\n{scores[0]}\n" \
                          f"Результаты ударов противника:\n{scores[1]}"
            keeper_text = f"❌ Ты пропустил гол\n@{get_username_by_id(res[1])} бил в другой угол\n" \
                          f"Результаты твоих ударов:\n{scores[1]}\n" \
                          f"Результаты ударов противника:\n{scores[0]}"
        elif res[1] != -1:
            kicker_text = f"❌ Увы ты не забил\n@{get_username_by_id(res[2])} угадал твой удар\n" \
                f"Результаты твоих ударов:\n{scores[0]}\n" \
                f"Результаты ударов противника:\n{scores[1]}"
            keeper_text = f"🏆 Ты отбил удар\n@{get_username_by_id(res[1])} бил в тот же угол\n" \
                f"Результаты твоих ударов:\n{scores[1]}\n" \
                f"Результаты ударов противника:\n{scores[0]}"
        finish = check_finish_game_penalti(call, res, scores)
        if not finish:
            try:
                bot.send_message(res[1], kicker_text)
            except UnboundLocalError as err:
                print("Ссылка на переменную происходит раньше ее определения")
                print(err)
            bot.send_message(res[2], keeper_text)
            pnt.change_kicker(res[2])
            bot.send_photo(res[1], open('images/keeper.png', 'rb'),
                           "Выбери угол, в который хочешь прыгнуть",
                           reply_markup=markup)
            bot.send_photo(res[2], open('images/keeper.png', 'rb'),
                           "Выбери угол, в который хочешь ударить",
                           reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "trade" in call.data)
def call_trade(call):
    if call.data == "trade_canc":
        trade_id = cfg.cancel_trade(call.message.chat.id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🎭 Обмен картами", callback_data="chan_by_0"))
        markup.add(tp.InlineKeyboardButton(
            text="🧑💻 В личный кабинет", callback_data="back"))
        if trade_id[0] == 0:
            msg = bot.send_message(call.message.chat.id,
                                   "❌ Вы отменили обмен!", reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
            return
        if trade_id[0] != call.message.chat.id:
            msg = bot.send_message(
                trade_id[0], "❌ Увы, сделка сорвалась.", reply_markup=markup)
            msg1 = bot.send_message(
                trade_id[1], "❌ Вы отменили обмен!", reply_markup=markup)
        else:
            msg = bot.send_message(
                trade_id[1], "❌ Увы, сделка сорвалась.", reply_markup=markup)
            msg1 = bot.send_message(
                trade_id[0], "❌ Вы отменили обмен!", reply_markup=markup)
        cfg.insert_lk_message_id(msg1.message_id, trade_id[0])
        cfg.insert_lk_message_id(msg.message_id, trade_id[1])

    if call.data == "trade":
        trade_id = cfg.do_trade(call.message.chat.id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🧳 Моя коллекция", callback_data="one_by_0"))
        markup.add(tp.InlineKeyboardButton(
            text="🧑💻 В личный кабинет", callback_data="back"))
        if trade_id[0] != call.message.chat.id:
            msg = bot.send_message(trade_id[0], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                   reply_markup=markup)
            msg1 = bot.send_message(trade_id[1], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                    reply_markup=markup)
        else:
            msg = bot.send_message(trade_id[1], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                   reply_markup=markup)
            msg1 = bot.send_message(trade_id[0], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                    reply_markup=markup)
        cfg.insert_lk_message_id(msg1.message_id, trade_id[0])
        cfg.insert_lk_message_id(msg.message_id, trade_id[1])


# обработка платежа пользователя
@bot.callback_query_handler(func=lambda call: call.data.isdigit() and int(call.data) < 7)
def get_buy_message(call):
    if call.data == "0":
        check_pay(call)
    else:
        cfg.clear_user_transaction(call.message.chat.id)
        operation_id = cfg.get_operation_id(call.message.chat.id, call.data)
        redirect_uri = pt.quick_pay(
            "buy cards", cfg.get_price(int(call.data)), operation_id)
        if int(call.data) != 4:
            cfg.place_operation_in_db(
                call.message.chat.id, operation_id, "Покупка случайных карточек")
        else:
            cfg.place_operation_in_db(
                call.message.chat.id, operation_id, "Покупка дополнительных ударов")
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(text="Оплатить", url=redirect_uri))
        markup.add(tp.InlineKeyboardButton(
            text="Проверить оплату", callback_data="check_pay"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        bot.edit_message_text(message_id=cfg.get_lk_id_message(call.message.chat.id), chat_id=call.message.chat.id,
                              text="Ваш заказ сформирован\nОплатите его по кнопке ниже",
                              reply_markup=markup)


# проверка оплаты заказа
@bot.callback_query_handler(func=lambda call: call.data == "check_pay")
def check_pay(call):
    free_card = cfg.check_free_card(call.message.chat.id)
    if call.data == "0" and free_card[0]:
        cfg.add_cards_to_user(cfg.get_random_card(1), call.message.chat.id)
        cfg.push_free_card_date(call.message.chat.id)
        # новая строчка кода ниже
        cfg.set_get_msg(call.message.chat.id, 0)
        show_new_card(call)
    elif call.data == "0" and not free_card[0]:
        ans = free_card[1].split(":")
        # изменена одна строчка ниже
        ans_str = ans[0] + "ч " + ans[1] + "мин ⏱️"
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🛍 Магазин карточек", callback_data="store"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        bot.edit_message_text(message_id=cfg.get_lk_id_message(call.message.chat.id), chat_id=call.message.chat.id,
                              text="Ты недавно получал свою бесплатную карточку! "
                                   "Следующую ты можешь получить через " + ans_str + ". "
                                   "Если не хочешь ждать - приобретай дополнительные карточки!",
                              reply_markup=markup)
    elif call.data != "0":
        print(call.data)
        operation_id = cfg.get_active_transaction(call.message.chat.id)
        if pt.check_payment(operation_id):
            # добавлена одна строчка кода ниже
            cfg.save_transaction(call.message.chat.id)
            product_id = operation_id.split("|")[1]
            if int(product_id) == 1:
                card_num = 1
            if int(product_id) == 2:
                card_num = 3
            if int(product_id) == 3:
                card_num = 5
            if int(product_id) == 4:
                ls.update_user_strikes(call.from_user.id, 1)
                markup = tp.InlineKeyboardMarkup()
                markup.add(tp.InlineKeyboardButton(
                    text="🎲 Мини-игры", callback_data="games"))
                bot.edit_message_text(message_id=call.message.message_id, chat_id=call.from_user.id,
                                      text="Успешно ✅, купленные удары уже начисленны вам,"
                                           "время проверить удачу!", reply_markup=markup)
                return
            cfg.add_cards_to_user(cfg.get_random_card(
                card_num), call.message.chat.id)
            cfg.plus_user_transactions(call.message.chat.id)
            markup = tp.InlineKeyboardMarkup()
            markup.add(
                tp.InlineKeyboardButton(text="\U0001F0CF Получить карточки \U0001F0CF", callback_data="get_new_cards"))
            bot.edit_message_text(message_id=cfg.get_lk_id_message(call.message.chat.id), chat_id=call.message.chat.id,
                                  text="Успешно ✅, получите ваш заказ", reply_markup=markup)


# демонстрация новых карточек, которые получил пользователь
# в процессе открытия набора
@bot.callback_query_handler(func=lambda call: call.data == "get_new_cards")
def show_new_card(call):
    card_info = cfg.get_last_cards(call.message.chat.id)
    if card_info[1] >= 1:
        ans = str(card_info[0][2]) + " aka " + str(card_info[0][3]) \
            + "\nРейтинг: " + str(card_info[0][6]) \
              + "\nКоманда: " + str(card_info[0][4]) + "\n" \
              + "Редкость: " + cfg.get_rareness_by_num(card_info[0][5])
        markup = tp.InlineKeyboardMarkup()
        if card_info[1] == 1:
            markup.add(tp.InlineKeyboardButton(
                text="✅ Принять", callback_data="new_lk"))
        else:
            markup.add(tp.InlineKeyboardButton(
                text="Дальше \U0001F449", callback_data="get_new_cards"))
        bot.send_photo(call.message.chat.id,
                       card_info[0][1], caption=ans, reply_markup=markup)


# этот хендлер был переписан (чтобы реализовать более удобную навигацию по управлению ботом)
@bot.callback_query_handler(func=lambda call: call.data == "admin")
def get_admin(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="Карточки", callback_data="admin_card"))
    markup.add(tp.InlineKeyboardButton(
        text="Промокоды", callback_data="admin_promo"))
    markup.add(tp.InlineKeyboardButton(
        text="Пользователи", callback_data="admin_users"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="back"))
    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                          text="Добро пожаловать в админскую панель\n"
                               "Выберете раздел с которым вы хотите работать",
                          reply_markup=markup)


# новый хендлер для навигации по управлению ботом
@bot.callback_query_handler(func=lambda call: "admin_" in call.data)
def admin_sections(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    section = call.data.split("_")[1]
    markup = tp.InlineKeyboardMarkup()
    if section != "users":
        add_btn = tp.InlineKeyboardButton(
            text="Добавить", callback_data="adm_add_" + section)
        del_btn = tp.InlineKeyboardButton(
            text="Удалить", callback_data="adm_del_" + section)
        markup.row(add_btn, del_btn)
        if section == "card":
            markup.row(tp.InlineKeyboardButton(
                text="Редактировать", callback_data="adm_update"))
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="admin"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы находитесь в разделе управления карточками!\n"
                                       "Выберете действие, которое хотите выполнить",
                                  reply_markup=markup)
        else:
            markup.row(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="admin"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы находитесь в разделе управления промокодами!\n"
                                       "Выберете действие, которое хотите выполнить",
                                  reply_markup=markup)
    else:
        markup.add(tp.InlineKeyboardButton(
            text="Инфо по юзеру", callback_data="get_user"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы находитесь в разделе управления пользователями!\n"
                                   "Выберете действие, которое хотите выбрать",
                              reply_markup=markup)


# новый хендлер для расширения функционала админ панели
@bot.callback_query_handler(func=lambda call: "get_user" in call.data)
def users_processing(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="⏪ Назад", callback_data="admin_users"))
    if call.data == "get_user":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Напишите @username пользователя, "
                                   "о котором хотите получить информацию",
                              reply_markup=markup)
        bot.register_next_step_handler(call.message, get_username_for_admin)
        return
    if "get_user_hist" in call.data:
        user_id = int(call.data.split("_")[3])
        ans_str = adm.get_user_transactions_info(
            user_id, get_username_by_id(user_id))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=ans_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("_")[0].isdigit() and int(call.data.split("_")[0]) >= 15)
def redact_card(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    msg_id = call.message.message_id
    card = cfg.get_card_by_id(int(call.data.split("_")[0]))[0]
    new_caption = card + \
        "\n\nОтправьте новые характеристики игрока в формате\n" \
        "1.Имя игрока\n2.Никнейм игрока\n3.Команда игрока\n4.Редкость карточки\n" \
        "5.Рейтинг карточки\n\nцифры указывать не надо"
    if call.message.caption is not None:
        new_caption = call.message.caption + "\n\nОтправьте новые характеристики игрока в формате\n" \
                                             "1.Имя игрока\n2.Никнейм игрока\n3.Команда игрока\n4.Редкость карточки\n" \
                                             "5.Рейтинг карточки\n\nцифры указывать не надо"
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=msg_id,
                             caption=new_caption)
    bot.register_next_step_handler(
        call.message, get_new_photo, int(call.data.split("_")[0]))


@bot.callback_query_handler(func=lambda call: "adm_" in call.data and cfg.is_admin(call.message.chat.id))
def admin_execute(call):
    if call.data == "adm_add_card":
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        bot.edit_message_text(message_id=cfg.get_lk_id_message(call.message.chat.id),
                              chat_id=call.message.chat.id,
                              text="Для начала укажите характеристики карточки в формате\n"
                                   "1.Имя игрока\n"
                                   "2.Никнейм игрока\n"
                                   "3.Команда игрока\n"
                                   "4.Редкость карточки\n"
                                   "5.Рейтинг карточки\n\n"
                                   "цифры указывать не надо",
                              reply_markup=markup)
        bot.register_next_step_handler(call.message, get_photo)
    if call.data == "adm_add_promo":
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        # были изменены аргументы этой вызываемой функции
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text="Напишите промокод, который хотите добавить"
                                   "\nЧтобы указать количество использований "
                                   "напишите это число через пробел от промокода",
                              reply_markup=markup)
        bot.register_next_step_handler(call.message, get_promo_text)
    if call.data == "adm_del_promo":
        markup = tp.InlineKeyboardMarkup()
        promos = adm.select_all_promos()
        print(promos)
        if promos is not None:
            for i in range(0, len(promos[0])):
                markup.add(tp.InlineKeyboardButton(text=str(promos[0][i][1]) + " - " + promos[1][i][2],
                                                   callback_data="promo_" + str(promos[0][i][0]) + "_del"))
            # изменена строчка кода ниже (убран таб)
            markup.add(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="admin"))
        else:
            markup.add(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="admin"))
            msg = bot.edit_message_text(chat_id=call.message.chat.id, text="Сейчас нет активных промокодов",
                                        message_id=call.message.message_id, reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
            return
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберете промокод для удаления\nВсе промокоды указаны в формате промокод - карточка",
                              reply_markup=markup)
    # исправлен код функции ниже
    if call.data == "adm_update":
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Выбрать карточку", callback_data="redact_62_0"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text="Тут можно выбрать карточку для редактирования, "
                                   "чтобы открыть просмотр нажмите на кнопку",
                              reply_markup=markup)
    if call.data == "adm_del_card":
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Выбрать карточку", callback_data="destroy_62_0"))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text="Тут можно выбрать карточку для удаления, "
                                   "чтобы открыть нажмите на кнопку",
                              reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "new_lk")
def get_new_lk(call):
    # добавлена новая проверка
    if not is_subscribed(call.message.chat.id):
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Подписаться \U00002705", url="https://t.me/offsidecard"))
        bot.send_message(message.from_user.id, "Чтобы начать необходимо подписаться на канал",
                         reply_markup=markup)
        return
    go_to_lk_message(call.message.chat.id)


# переписана эта функция (добавлены новые функции управления ботом)
@bot.callback_query_handler(func=lambda call: "choose_" in call.data or "redact_" in call.data or "destroy_" in call.data)
def show_all_cards(call):
    num = int(call.data.split("_")[2])
    card_list = adm.select_all_cards()
    markup = tp.InlineKeyboardMarkup()
    if "choose_" in call.data:
        promo_id = int(call.data.split("_")[1])
        next_btn = tp.InlineKeyboardButton(
            text=">>", callback_data="choose_" + str(promo_id) + "_" + str(num + 1))
        back_btn = tp.InlineKeyboardButton(
            text="<<", callback_data="choose_" + str(promo_id) + "_" + str(num - 1))
        choose_btn = tp.InlineKeyboardButton(text="Выбрать в промо",
                                             callback_data="promo_" + str(promo_id) + "_" + str(card_list[num][0]))
    if "redact_" in call.data:
        card_id = 62
        next_btn = tp.InlineKeyboardButton(
            text=">>", callback_data="redact_" + str(card_id) + "_" + str(num + 1))
        back_btn = tp.InlineKeyboardButton(
            text="<<", callback_data="redact_" + str(card_id) + "_" + str(num - 1))
        choose_btn = tp.InlineKeyboardButton(
            text="Выбрать для редактирования", callback_data=str(card_list[num][0]) + "_old")
    if "destroy_" in call.data:
        card_id = 62
        next_btn = tp.InlineKeyboardButton(
            text=">>", callback_data="destroy_" + str(card_id) + "_" + str(num + 1))
        back_btn = tp.InlineKeyboardButton(
            text="<<", callback_data="destroy_" + str(card_id) + "_" + str(num - 1))
    num_btn = tp.InlineKeyboardButton(
        text='(' + str(num + 1) + '/' + str(len(card_list)) + ')', callback_data="...")
    msg_id = cfg.get_lk_id_message(call.message.chat.id)
    if "destroy_" not in call.data:
        markup.row(choose_btn)
    else:
        del_btn = tp.InlineKeyboardButton(
            text="Удалить", callback_data="delete_card_" + str(card_list[num][0]))
        markup.row(del_btn)
    if num == 0:
        markup.row(num_btn, next_btn)
        if call.message.photo is None:
            msg = bot.send_photo(call.message.chat.id,
                                 card_list[num][1], reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)
        else:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=msg_id,
                                   media=tp.InputMediaPhoto(card_list[num][1]), reply_markup=markup)
    elif num == len(card_list) - 1:
        markup.row(back_btn, num_btn)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=msg_id,
                               media=tp.InputMediaPhoto(card_list[num][1]), reply_markup=markup)
    else:
        markup.row(back_btn, num_btn, next_btn)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=msg_id,
                               media=tp.InputMediaPhoto(card_list[num][1]), reply_markup=markup)


# новый хендлер для удаления карточек
@bot.callback_query_handler(func=lambda call: "delete_card" in call.data)
def delete_card(call):
    card_id = call.data.split("_")[2]
    adm.delete_card(card_id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="admin"))
    msg = bot.send_message(call.message.chat.id, "Карточка была успешно удалена",
                           reply_markup=markup)
    cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: "promo_" in call.data)
def add_card_to_promo(call):
    promo_id = call.data.split("_")[1]
    if call.data.split("_")[2] == "del":
        adm.delete_promo(promo_id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Промокод был успешно удален", reply_markup=markup)
        return
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="🧑💻 В личный кабинет", callback_data="back"))
    markup.add(tp.InlineKeyboardButton(
        text="К получению карточек", callback_data="getcar"))
    if call.data.split("_")[2] == "rng":
        adm.insert_promo_card(promo_id, 0)
    else:
        info = call.data.split("_")
        card_id = info[2]
        adm.insert_promo_card(promo_id, card_id)
    msg = bot.send_message(call.message.chat.id, "Промокод был успешно добавлен! Время его проверить",
                           reply_markup=markup)
    cfg.insert_lk_message_id(msg.message_id, call.message.chat.id)


def check_promocode(message):
    res = adm.check_promo(message.chat.id, message.text)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="🧑💻 В личный кабинет", callback_data="back"))
    markup.add(tp.InlineKeyboardButton(text="⏪ Назад", callback_data="getcar"))
    if res[0]:
        # тело этого if было изменено
        if res[1] == 0:
            cfg.add_cards_to_user(cfg.get_random_card(1), message.chat.id)
        else:
            adm.add_card_to_user_by_card_id(res[1], message.chat.id)
        adm.minus_promo_usages(message.text)
        get_show_new_cards(message)
        # конец изменений
    else:
        msg = bot.send_message(message.chat.id, "Увы, но такого промокода не существует, либо он больше недействительный😔",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.chat.id)


# эта функция переписана
def get_promo_text(message):
    promo = message.text.split(" ")[0]
    if len(message.text.split(" ")) > 1:
        usages = message.text.split(" ")[1]
    else:
        usages = "INF"
    promo_id = adm.place_promo(promo, usages)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(text="Выбрать карточку",
               callback_data="choose_" + str(promo_id) + "_0"))
    markup.add(tp.InlineKeyboardButton(text="Рандомная карточка",
               callback_data="promo_" + str(promo_id) + "_rng"))
    bot.send_message(message.chat.id, "Теперь нажмите кнопку выбрать карточку, "
                                      "чтобы она выдавалась при вводе промокода", reply_markup=markup)


def get_second_user_for_offer(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    username = message.text.replace("@", "")
    # изменена одна строчка ниже
    user_id = search_user_by_username(username, message.chat.id)
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="🧑💻 В личный кабинет", callback_data="new_lk"))
    if user_id == -1:
        bot.send_message(message.from_user.id,
                         "Этому пользователю нельзя предложить обмен, попробуйте снова",
                         reply_markup=markup)
    else:
        cfg.insert_second_user(message.chat.id, user_id)
        card = cfg.get_trade_card(message.chat.id, 0)
        msg = bot.send_message(message.from_user.id, "✅ Предложение обмена успешно отправлено "
                                                     "пользователю - @" + username)
        cfg.insert_lk_message_id(msg.message_id, message.chat.id)
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="🃏 Выбрать карту для обмена", callback_data="chan_by_0"))
        markup.add(tp.InlineKeyboardButton(
            text="❌ Отклонить обмен", callback_data="trade_canc"))
        msg = bot.send_photo(chat_id=user_id, photo=card[1],
                             caption="Вам поступило предложение обмена от - @" +
                             get_username_by_id(message.chat.id),
                             reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, user_id)


def get_username_for_pen(message):
    # изменена одна строчка кода ниже
    tele_id2 = search_user_by_username(message.text, message.from_user.id)
    if tele_id2 == -1:
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="back"))
        msg = bot.send_message(message.chat.id, "Этому пользователю нельзя предложить игру в Пенальти ☹️\n"
                                                "Ему нужно запустить этого бота и получить свою первую карточку!",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.chat.id)
    else:
        # ниже добавлена проверка на разницу в рейтинге
        if pnt.check_delta_rating(message.chat.id, tele_id2):
            markup = tp.InlineKeyboardMarkup()
            markup.add(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="back"))
            msg = bot.send_message(message.chat.id,
                                   "Ты не можешь сыграть в пенальти с " + message.text +
                                   " из-за большой разницы в рейтинге☹️",
                                   reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, message.chat.id)
            return
        markup = tp.InlineKeyboardMarkup()
        if not pnt.user_in_game(tele_id2):
            pnt.create_game(message.chat.id)
            pnt.insert_second_user(tele_id2, message.chat.id)

            markup.add(tp.InlineKeyboardButton(
                text="✅ Начать игру", callback_data="pen_start"))
            markup.add(tp.InlineKeyboardButton(
                text="❌ Отклонить", callback_data="pen_canc"))
            msg = bot.send_message(tele_id2,
                                   "@" +
                                   get_username_by_id(
                                       message.chat.id) + " предлагает вам сыграть в Пенальти!",
                                   reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, tele_id2)
            bot.send_message(
                message.chat.id, "📩Ваше предложение сыграть в Пенальти было отправлено " + message.text + "!")
        else:
            markup.add(tp.InlineKeyboardButton(
                text="ПЕНАЛЬТИ⚽️", callback_data="penalti"))
            markup.add(tp.InlineKeyboardButton(
                text="⏪ Назад", callback_data="back"))
            msg = bot.send_message(message.chat.id, "Этому пользователю нельзя предложить игру в Пенальти ☹️\n"
                                                    "Он уже находиться в игре, дождитесь конца или предложите игру кому-нибудь другому",
                                   reply_markup=markup)
            cfg.insert_lk_message_id(msg.message_id, message.from_user.id)


# новая функция для получения юзернейма (для получения инфы о нем)
def get_username_for_admin(message):
    user_id = search_user_by_username(message.text, -1)
    markup = tp.InlineKeyboardMarkup()
    if user_id == -1:
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin_users"))
        bot.send_message(message.chat.id, "Пользователь с таким именем не был найден. "
                                          "Проверьте корректность ввода данных",
                         reply_markup=markup)
    else:
        markup.add(tp.InlineKeyboardButton(text="История покупок",
                   callback_data="get_user_hist_" + str(user_id)))
        markup.add(tp.InlineKeyboardButton(
            text="⏪ Назад", callback_data="admin_users"))
        user_str = adm.get_user_info(user_id, message.text)
        msg = bot.send_message(
            message.chat.id, text=user_str, reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.chat.id)


def get_photo(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    player_info = message.text.split("\n")
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="Вернуться к панели", callback_data="admin"))
    card = cfg.place_player_in_db(player_info)
    if card is not None and cfg.check_card_info(player_info) != -1:
        bot.send_message(message.from_user.id,
                         "Теперь отправьте фото карточки игрока")
        bot.register_next_step_handler(message, save_card_photo, card[0])
    else:
        msg = bot.send_message(message.from_user.id, "Некорректный ввод данных, попробуйте снова",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)
        bot.register_next_step_handler(message, get_photo)


def save_card_photo(message, card_id):
    if cfg.set_card_photo(card_id, message.photo[0].file_id) != -1:
        # исправлено тело этого if
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Сохранить", callback_data="new_lk"))
        markup.add(tp.InlineKeyboardButton(
            text="Редактировать", callback_data=str(card_id) + "_new"))
        new_card = cfg.get_card_by_id(card_id)
        bot.send_photo(message.from_user.id,
                       new_card[1], caption=new_card[0], reply_markup=markup)
    else:
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="В админскую панель", callback_data="admin"))
        msg = bot.send_message(
            message.from_user.id, "Произошла какая-то ошибка, уже работаем над этим")
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)


def get_new_photo(message, card_id):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    player_info = message.text.split("\n")
    markup = tp.InlineKeyboardMarkup()
    markup.add(tp.InlineKeyboardButton(
        text="Вернуться к панели", callback_data="admin"))
    card = cfg.edit_card_in_db(card_id, player_info)
    if card is not None and cfg.check_card_info(player_info) != -1:
        markup.add(tp.InlineKeyboardButton(
            text="Пропустить редактирование фото", callback_data="admin"))
        msg = bot.send_message(
            message.from_user.id, "Теперь отправьте фото карточки игрока", reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)
        bot.register_next_step_handler(message, save_new_card_photo, card_id)
    else:
        msg = bot.send_message(message.from_user.id, "Некорректный ввод данных, попробуйте снова",
                               reply_markup=markup)
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)
        bot.register_next_step_handler(message, get_new_photo, card_id)


def save_new_card_photo(message, card_id):
    if cfg.set_card_photo(card_id, message.photo[0].file_id) != -1:
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="Сохранить", callback_data="admin"))
        new_card = cfg.get_card_by_id(card_id)
        bot.send_photo(message.from_user.id,
                       new_card[1], caption=new_card[0], reply_markup=markup)
        msg = bot.send_message(message.from_user.id, ".")
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)
    else:
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="В админскую панель", callback_data="admin"))
        msg = bot.send_message(
            message.from_user.id, "Произошла какая-то ошибка, уже работаем над этим")
        cfg.insert_lk_message_id(msg.message_id, message.from_user.id)


# новая функция для получения бесплатной карточке при промокоде
def get_show_new_cards(message):
    card_info = cfg.get_last_cards(message.chat.id)
    if card_info[1] >= 1:
        ans = str(card_info[0][2]) + " " + str(card_info[0][3]) \
            + "\nРейтинг: " + str(card_info[0][6]) \
              + "\nКоманда: " + str(card_info[0][4]) + "\n" \
              + "Редкость: " + cfg.get_rareness_by_num(card_info[0][5])
        markup = tp.InlineKeyboardMarkup()
        markup.add(tp.InlineKeyboardButton(
            text="✅ Принять", callback_data="new_lk"))
        bot.send_photo(message.chat.id,
                       card_info[0][1], caption=ans, reply_markup=markup)


# переписанный участок кода, тут надо найти timer в основном коде и заменить на это
time_checker = threading.Thread(target=time_events_checker)
time_checker.start()

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})


cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
