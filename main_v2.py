import asyncio
import datetime
import glob
import logging
import os
import random
import string
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ContentType, \
    InputFile
from aiogram import F

from Keyboards.UserKeyboards import InlineButtons
from config import *
from lucky_strike import *
from main_config import token, CHANNEL_ID
from penalti import *
from timers import *

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()

CHANNEL_ID = CHANNEL_ID

async def is_subscribed(USER_ID):
    member = await bot.get_chat_member(CHANNEL_ID, USER_ID)
    if member.status not in ['left', 'kicked']:
        return True
    else:
        return False

async def get_username_by_id(tele_id):
    user = await bot.get_chat_member(CHANNEL_ID, tele_id)
    username = user.username
    return str(username)


@dp.message(Command("start"))
async def start_message(message: types.Message, state: FSMContext):
    await clear_non_active_users()

    if not await is_subscribed(message.from_user.id):

        await message.answer("Чтобы начать играть, необходимо:\n"
                             "1️⃣ Подписаться на канал @offsidecard\n"
                             "2️⃣ Нажать на /start", reply_markup=InlineButtons.start_kb__not_sub())

    elif not await check_spam(message.from_user.id):

        await place_user_in_bd(message.from_user.id)
        sent_msg = await message.answer("👋 *Добро пожаловать в OFFSide*\n\n"
                                        "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                                        "из медиафутбола и играть в мини-игры.\n\n"
                                        "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                                        "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                                        "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                                        "Все правила игры вы можете узнать в разделе: *«ℹ️ Информация»*\n\n"
                                        "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                                        reply_markup=InlineButtons.start_kb__sub(), parse_mode='Markdown')
        await insert_lk_message_id(sent_msg.message_id, message.from_user.id)

@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    await clear_non_active_users()
    await callback.message.edit_text("👋 *Добро пожаловать в OFFSide*\n\n"
                         "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                         "из медиафутбола и играть в мини-игры.\n\n"
                         "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                         "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                         "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                         "Все правила игры вы можете узнать в разделе: *«ℹ️ Информация»*\n\n"
                         "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                         reply_markup=InlineButtons.start_kb__sub(), parse_mode='Markdown')

@dp.callback_query(F.data == "info")
async def answer_info_callback(callback: types.CallbackQuery):

    await callback.message.edit_text(text="В этом разделе можно найти информацию про наш проект", reply_markup=InlineButtons.info_kb())

# сообщение с получением более подробной информации
@dp.callback_query(F.data[-5:] == "_info")
async def answer_questions(callback: types.CallbackQuery):


    if callback.data == "card_info":
        await callback.message.edit_text("Каждая карта имеет свою редкость и количество баллов, которые она добавляет к твоему рейтингу:\n\n"
                                   "1) Легендарная редкость: Карта добавляет 1000 баллов к твоей коллекции.\n\n"
                                   "2) Уникальная редкость: Карта добавляет 500 баллов к твоей коллекции.\n\n"
                                   "3) Эпическая редкость: Карта добавляет 250 баллов к твоей коллекции.\n\n"
                                   "4) Необычная редкость: Карта добавляет 100 баллов к твоей коллекции.\n\n"
                                   "5) Обычная редкость: Карта добавляет 50 баллов к твоей коллекции.\n\n",
                              reply_markup=InlineButtons.back_kb())
    if callback.data == "penalti_info":
        await callback.message.edit_text("Игра в пенальти, это отдельный режим в OFFSIDE, "
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
                              reply_markup=InlineButtons.back_kb())
    if callback.data == "strike_info":
        await callback.message.edit_text("Чтобы начать игру в удачный удар, вам нужно:\n"
                                   "1. Зайти в раздел  «🎲 Мини-игры»\n"
                                   "2. Выбрать игру «☘️ Удачный удар»\n"
                                   "3. Нажать на кнопку «⚽️ Сделать удар»\n\n"
                                   "☘️ Удачный удар - это мини-игра, в которой ты делаешь 1 удар по воротам.\n"
                                   "Если забиваешь - получаешь одну рандомную карточку.\n"
                                   "Если не забиваешь - пробуешь еще через 4 часа.\n"
                                   "В день доступно 2 бесплатные попытки.\n"
                                   "Если тебе сегодня везет и хочешь сделать больше ударов по воротам - "
                                   "можешь приобрести дополнительные попытки.",
                              reply_markup=InlineButtons.back_kb())


# обработка callback'a для личного кабинета
@dp.callback_query(F.data == "back")
async def return_to_lk(callback: types.CallbackQuery):

    await calc_card_rating(callback.from_user.id)
    await cancel_trade(callback.from_user.id)

    user = await search_user_in_db(callback.from_user.id)

    stat_str = "Твои достижения:\n\n🃏 Собранное количество карточек: " + str(user.card_num) + "\n" \
                "🏆 Рейтинг собранных карточек:" + str(user.card_rating) + "\n\n" \
                "⚽️ Рейтинг в игре Пенальти: " + str(user.penalty_rating)

    await callback.message.edit_text(stat_str, reply_markup=InlineButtons.back_lk_kb(await is_admin(callback.from_user.id)))


@dp.callback_query(F.data == "rate")
async def get_player_rating(callback: types.CallbackQuery):
    await calc_card_rating(callback.from_user.id)

    await callback.message.edit_text("В этом разделе ты можешь посмотреть 🏆Топ 10 игроков по категориям!",
                          reply_markup=InlineButtons.rate_kb())


@dp.callback_query(F.data[:5] == "rate_")
async def get_top_places(callback: types.CallbackQuery):
    num = 1
    ans_str = ""

    places = get_user_places(callback.from_user.id)

    if callback.data == "rate_card":
        card_top = get_top_places_()[0]
        for user in card_top:
            ans_str += str(num) + ". @" + await get_username_by_id(user.tele_id) \
                + " - " + str(user.card_rating) + "\n"
            num += 1
        if not user_in_top_ten(callback.from_user.id)[0]:
            user = search_user_in_db(callback.from_user.id)
            ans_str += "\n" + str(places[0]) + ". @" + callback.from_user.username + \
                " - " + str(user.card_rating)

    if callback.data == "rate_pen":
        penalti_top = get_top_places_()[1]
        for user in penalti_top:
            ans_str += str(num) + ". @" + await get_username_by_id(user.tele_id) \
                + " - " + str(user.penalty_rating) + "\n"
            num += 1
        if not user_in_top_ten(callback.from_user.id)[1]:
            user = search_user_in_db(callback.from_user.id)
            ans_str += "\n" + str(places[1]) + ". @" \
                       + callback.from_user.username + \
                " - " + str(user.penalty_rating)

    await callback.message.edit_text(ans_str, reply_markup=InlineButtons.back_kb())



@dp.callback_query(F.data == "coll")
async def get_collection(callback: types.CallbackQuery):
    user_cards = get_user_card_list(callback.from_user.id)

    if user_cards is None:

        await callback.message.edit_text("Пока что ваша коллекция пуста", reply_markup=InlineButtons.take_card_kb(have_cards=False))
    else:

        ans_str = "Список всех ваших карт: \n\n"
        num = 1
        await calc_card_rating(callback.from_user.id)

        for i in range(0, len(user_cards[0])):
            ans_str += str(num) + ". " + str(user_cards[0][i].player_name) + " (" + str(user_cards[0][i].player_nickname) + ") - " + \
                str(user_cards[1][i].num) + " шт.\n"
            num += 1
        msg = await callback.message.answer(ans_str, reply_markup=InlineButtons.take_card_kb(have_cards=True))

        await insert_lk_message_id(msg.message_id, callback.from_user.id)


# вызов мини-игр
@dp.callback_query(F.data == "games")
async def get_mini_games(callback: types.CallbackQuery):

    await callback.message.edit_text("Тут находятся мини-игры, в которые можешь поиграть с друзьями и выяснить, кто из вас лучший🥇",
                          reply_markup=InlineButtons.games_kb())


@dp.callback_query(F.data == "penalti")
async def penalti_message(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)

    if not user_in_game(callback.from_user.id):
        await callback.message.edit_text("✉️ Напишите @username пользователя, которому хотите предложить игру в Пенальти",
                              reply_markup=InlineButtons.back_kb())
        # bot.register_next_step_handler(call.message, get_username_for_pen)
    else:
        await callback.message.edit_text("Вы уже состоите в игре, закончите ее, чтобы начать следующую",
                              reply_markup=InlineButtons.back_kb())

@dp.callback_query(F.data == "lucky_strike")
async def lucky_strike(callback: types.CallbackQuery):

    msg = await callback.message.edit_text("☘️ Удачный удар - это мини-игра, в которой ты делаешь 1 удар по воротам. "
                                     "Если забиваешь - получаешь одну рандомную карточку.Если не забиваешь - "
                                     "пробуешь еще через время",
                                reply_markup=InlineButtons.lucky_strike_kb())
    await insert_lk_message_id(msg.message_id, callback.from_user.id)


# функция игры удачный удар
@dp.callback_query(F.data == "do_strike")
async def do_strike(callback: types.CallbackQuery):
    free_info = check_free_strike(callback.from_user.id)
    purchased = check_purchased_strikes(callback.from_user.id)

    tasks = []

    if free_info[0] or purchased[0]:
        msg = await callback.message.answer_dice('⚽️')
        if msg.dice.value < 3:

            await update_user_strikes(callback.from_user.id, -1)

            if not purchased[0] or purchased[1] == 1:
                msg_text = "☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           "Попробуй еще раз через 4 часа или получи 3 удара за 100 рублей!"
                tasks.append("b3")
            else:
                msg_text = f"☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           f"У тебя осталось еще несколько попыток - {purchased[1] - 1}"
                tasks.append("no_b3")

            tasks.append("back")

        else:
            await update_user_strikes(callback.from_user.id, -1)
            await add_cards_to_user(get_random_card(1), callback.from_user.id)

            msg_text = "☘️ Ты испытал удачу и выиграл одну случайную карточку!"
            tasks.append("take_card")

        msg = await callback.message.answer(msg_text, reply_markup=InlineButtons.do_strike_kb(tasks))

        await insert_lk_message_id(msg.message_id, callback.from_user.id)
    elif not purchased[0]:

        msg_text = f"Ты недавно пробовал проверить свою удачу!\n" \
                   f"Приходи через {free_info[1].split(':')[0]}ч {free_info[1].split(':')[1]}мин" \
                   f" ⏱ или получи 3 удара за 100 рублей!"

        tasks.append("b3")
        tasks.append("back")

        await callback.message.edit_text(msg_text, reply_markup=InlineButtons.do_strike_kb(tasks))


async def main():

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())



