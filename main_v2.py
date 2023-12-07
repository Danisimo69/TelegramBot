import logging
import uuid

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram import F

from States.UserStates import *
from Filters.UserFilters import Has_One_Chan_Filter, Get_Buy_Message_Filter, Redact_Card_Filter, \
    Show_All_Cards_Filter
from Keyboards.UserKeyboards import InlineButtons
from Keyboards.AdminKeyboards import InlineButtons as AdminInlineKeyboard
from Modules.admin import get_user_transactions_info, select_all_promos, select_all_cards, delete_card_, delete_promo, \
    insert_promo_card, get_user_info, minus_promo_usages, add_card_to_user_by_card_id, place_promo, \
    check_promo_

from Modules.config import *
from Modules.lucky_strike import *
from main_config import token, CHANNEL_ID
from Modules.payment import quick_pay, check_payment
from Modules.penalti import *
from Modules.timers import *

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
    username = user.user.username
    return str(username)


@dp.message(Command("start"))
async def start_message(message: types.Message, state: FSMContext):

    # print("START")

    await state.clear()

    await clear_non_active_users()

    subs_status = await is_subscribed(message.from_user.id)
    spam_status = await check_spam(message.from_user.id)

    await bot.send_message(649811235, f"{message.from_user.id}, {subs_status}, {spam_status}")

    if not subs_status:

        await message.answer("Чтобы начать играть, необходимо:\n"
                             "1️⃣ Подписаться на канал @offsidecard\n"
                             "2️⃣ Нажать на /start", reply_markup=InlineButtons.start_kb__not_sub())

    elif not spam_status:

        await place_user_in_bd(message.from_user.id, message.from_user.username)
        await update_user_username(message.from_user.id, message.from_user.username)


        sent_msg = await message.answer("👋 *Добро пожаловать в OFFSide*\n\n"
                                        "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                                        "из медиафутбола и играть в мини-игры.\n\n"
                                        "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                                        "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                                        "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                                        "Все правила игры вы можете узнать в разделе: \n*«ℹ️ Информация»*\n\n"
                                        "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                                        reply_markup=InlineButtons.start_kb__sub(), parse_mode='Markdown')




@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    await clear_non_active_users()
    await callback.message.edit_text("👋 *Добро пожаловать в OFFSide*\n\n"
                                     "⚽️ Здесь ты сможешь собирать карточки своих любимых футболистов "
                                     "из медиафутбола и играть в мини-игры.\n\n"
                                     "🏆 У нас есть таблицы рейтинга среди коллекционеров карточек и игроков "
                                     "в мини-игры! Приобретай карточки и побеждай в мини-играх, "
                                     "чтобы подняться в рейтинге и обойти своих друзей.\n\n"
                                     "Все правила игры вы можете узнать в разделе: \n*«ℹ️ Информация»*\n\n"
                                     "Если ты готов к игре, то нажимай\n*«🎮 Начать игру»*",
                                     reply_markup=InlineButtons.start_kb__sub(), parse_mode='Markdown')


@dp.callback_query(F.data == "info")
async def answer_info_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(text="В этом разделе можно найти информацию про наш проект",
                                     reply_markup=InlineButtons.info_kb())


# сообщение с получением более подробной информации
@dp.callback_query(F.data[-5:] == "_info")
async def answer_questions(callback: types.CallbackQuery):
    if callback.data == "card_info":
        await callback.message.edit_text(
            "Каждая карта имеет свою редкость и количество баллов, которые она добавляет к твоему рейтингу:\n\n"
            "1) Легендарная редкость: Карта добавляет 1000 баллов к твоей коллекции.\n\n"
            "2) Уникальная редкость: Карта добавляет 500 баллов к твоей коллекции.\n\n"
            "3) Эпическая редкость: Карта добавляет 250 баллов к твоей коллекции.\n\n"
            "4) Необычная редкость: Карта добавляет 100 баллов к твоей коллекции.\n\n"
            "5) Обычная редкость: Карта добавляет 50 баллов к твоей коллекции.\n\n",
            reply_markup=InlineButtons.back_to_info_kb())
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
                                         reply_markup=InlineButtons.back_to_info_kb())
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
                                         reply_markup=InlineButtons.back_to_info_kb())


# обработка callback'a для личного кабинета
@dp.callback_query(F.data == "back")
async def return_to_lk(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await bot.answer_callback_query(callback.id)

    await calc_card_rating(callback.from_user.id)
    await cancel_trade(callback.from_user.id)

    user = await search_user_in_db(callback.from_user.id)

    stat_str = "Твои достижения:\n\n🃏 Собранное количество карточек: " + str(user.card_num) + "\n" \
                                                                                              "🏆 Рейтинг собранных карточек: " + str(
        user.card_rating) + "\n\n" \
                            "⚽️ Рейтинг в игре Пенальти: " + str(user.penalty_rating)

    try:
        await callback.message.edit_text(stat_str,
                                         reply_markup=InlineButtons.back_lk_kb(await is_admin(callback.from_user.id)))
    except:
        await callback.message.delete()
        await callback.message.answer(stat_str,
                                      reply_markup=InlineButtons.back_lk_kb(await is_admin(callback.from_user.id)))


@dp.callback_query(F.data == "rate")
async def get_player_rating(callback: types.CallbackQuery):
    await calc_card_rating(callback.from_user.id)

    await callback.message.edit_text("В этом разделе ты можешь посмотреть 🏆 Топ 10 игроков по категориям!",
                                     reply_markup=InlineButtons.rate_kb())


@dp.callback_query(F.data[:5] == "rate_")
async def get_top_places(callback: types.CallbackQuery):
    num = 1
    ans_str = ""

    places = await get_user_places(callback.from_user.id)

    if callback.data == "rate_card":

        ans_str += "🏆 Рейтинг игроков по картам\n\n"

        card_top = (await get_top_places_())[0]
        for user in card_top:
            ans_str += ("🥇" if str(num) == "1" else "🥈" if str(num) == "2" else "🥉" if str(num) == "3" else " " + str(
                num) + ".") + " @" + await get_username_by_id(user.tele_id) \
                       + " - " + str(user.card_rating) + "\n"
            num += 1
        if not (await user_in_top_ten(callback.from_user.id))[0]:
            user = await search_user_in_db(callback.from_user.id)
            ans_str += "\n" + str(places[0]) + ". @" + callback.from_user.username + \
                       " - " + str(user.card_rating)

    if callback.data == "rate_pen":
        ans_str += "🏆 Рейтинг игроков по пенальти\n\n"

        penalti_top = (await get_top_places_())[1]
        for user in penalti_top:
            ans_str += ("🥇" if str(num) == "1" else "🥈" if str(num) == "2" else "🥉" if str(num) == "3" else " " + str(
                num) + ".") + " @" + await get_username_by_id(user.tele_id) \
                       + " - " + str(user.penalty_rating) + "\n"
            num += 1
        if not (await user_in_top_ten(callback.from_user.id))[1]:
            user = await search_user_in_db(callback.from_user.id)
            ans_str += "\n" + str(places[1]) + ". @" \
                       + callback.from_user.username + \
                       " - " + str(user.penalty_rating)

    await callback.message.edit_text(ans_str, reply_markup=InlineButtons.back_kb())


@dp.callback_query(F.data == "coll")
async def get_collection(callback: types.CallbackQuery):
    user_cards = await get_user_card_list(callback.from_user.id)

    if user_cards == None:

        await callback.message.edit_text("Пока что ваша коллекция пуста",
                                         reply_markup=InlineButtons.take_card_kb(have_cards=False))
    else:

        ans_str = "Список всех ваших карт: \n\n"

        await calc_card_rating(callback.from_user.id)

        for i in range(0, len(user_cards[0])):

            card_id = user_cards[0][i].card_id
            info = 0
            for j in user_cards[1]:
                if j["id"] == card_id:
                    info = j["count"]
                    break

            ans_str += str(user_cards[0][i].player_nickname) + " | " + "Рейтинг: " + str(
                user_cards[0][i].points) + " | " + \
                       str(info) + " шт.\n"


        await callback.message.delete()
        msg = await callback.message.answer(ans_str, reply_markup=InlineButtons.take_card_kb(have_cards=True))




# вызов мини-игр
@dp.callback_query(F.data == "games")
async def get_mini_games(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Тут находятся мини-игры, в которые можешь поиграть с друзьями и выяснить, кто из вас лучший🥇",
        reply_markup=InlineButtons.games_kb())


@dp.callback_query(F.data == "penalti")
async def penalti_message(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    if not await user_in_game(callback.from_user.id):
        await callback.message.edit_text(
            "✉️ Напишите @username пользователя, которому хотите предложить игру в Пенальти",
            reply_markup=InlineButtons.back_kb())
        await state.set_state(UserState.get_username_for_pen.state)
    else:
        await callback.message.edit_text("Вы уже состоите в игре, закончите ее, чтобы начать следующую",
                                         reply_markup=InlineButtons.back_kb())


@dp.callback_query(F.data == "lucky_strike")
async def lucky_strike(callback: types.CallbackQuery):
    msg = await callback.message.edit_text("☘️ Удачный удар - это мини-игра, в которой ты делаешь 1 удар по воротам. "
                                           "Если забиваешь - получаешь одну рандомную карточку. Если не забиваешь - "
                                           "пробуешь еще через время",
                                           reply_markup=InlineButtons.lucky_strike_kb())



# функция игры удачный удар
@dp.callback_query(F.data == "do_strike")
async def do_strike(callback: types.CallbackQuery):
    await callback.message.delete()

    free_info = await check_free_strike(callback.from_user.id)
    purchased = await check_purchased_strikes(callback.from_user.id)

    tasks = []

    if free_info[0] or purchased[0]:
        msg = await callback.message.answer_dice('⚽️')
        await asyncio.sleep(4)
        if msg.dice.value < 3:

            await update_user_strikes(callback.from_user.id, -1)

            if not purchased[0] or purchased[1] == 1:
                msg_text = "☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           "Попробуй еще раз через 4 часа или получи 3 удара за 100 рублей!"
                tasks.append("b3")
            else:
                msg_text = f"☘️ Ты испытал удачу и сейчас тебе не повезло😔\n" \
                           f"Количество оставшихся попыток - {purchased[1] - 1}"
                tasks.append("no_b3")

            tasks.append("back")

        else:
            await update_user_strikes(callback.from_user.id, -1)
            await add_cards_to_user(await get_random_card(1, "lucky_strike"), callback.from_user.id)

            msg_text = "☘️ Ты испытал удачу и выиграл одну случайную карточку!"
            tasks.append("take_card")

        msg = await callback.message.answer(msg_text, reply_markup=InlineButtons.do_strike_kb(tasks))


    elif not purchased[0]:

        msg_text = f"Ты недавно пробовал проверить свою удачу!\n" \
                   f"Приходи через {free_info[1].split(':')[0]}ч {free_info[1].split(':')[1]}мин" \
                   f" ⏱ или получи 3 удара за 100 рублей!"

        tasks.append("b3")
        tasks.append("back")

        await callback.message.answer(msg_text, reply_markup=InlineButtons.do_strike_kb(tasks))


@dp.callback_query(F.data == "cont_off")
async def continue_offer(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)

    await callback.message.edit_text(text="Введите юзернейм пользователя, с которым хотите поменяться")

    # bot.register_next_step_handler(callback.message, get_offer_to_user)


@dp.callback_query(F.data == "getcar")
async def get_cards(callback: types.CallbackQuery):
    # bot.clear_step_handler_by_chat_id(callback.from_user.id)

    product_str = "🃏 Если ты хочешь получить карточку, то ты попал куда надо!\n\n" \
                  "Раз в 24 часа ты можешь получать одну карточку бесплатно, " \
                  "но если ты хочешь продвигаться по таблице рейтинга быстрее других" \
                  " и пополнять свою коллекцию, то рекомендуем тебе посетить магазин карт 🛍"

    await callback.message.edit_text(text=product_str, reply_markup=InlineButtons.getcar_kb())


# новый хендлер для перехода в магазин карточек
@dp.callback_query(F.data == "store")
async def get_card_shop(callback: types.CallbackQuery):
    await callback.message.edit_text(text="🛍 Ты находишься в магазине карт, у нас есть несколько товаров:\n\n"
                                          "💰 Одна рандомная карточка - 70 рублей\n"
                                          "💰 Три рандомных карточки - 190 рублей\n"
                                          "💰 Пять рандомных карточек - 275 рублей",
                                     reply_markup=InlineButtons.store_kb())


@dp.callback_query(F.data == "input")
async def wait_promo(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text("Введите промокод ниже", reply_markup=InlineButtons.back_to_getcar_kb())
    await state.set_state(UserState.check_promo.state)


@dp.callback_query(F.data[:13] == "my_collection")
async def my_collection(callback: types.CallbackQuery, state: FSMContext):
    try:
        dat = callback.data.split(":")[-1]
    except:
        dat = ""

    try:
        await callback.message.edit_text(
            "🎭 Выберите формат отображения коллекции" if dat != "chan" else "🧳 Выберите формат отображения коллекции"
            , reply_markup=InlineButtons.collection_kb(False if dat != "chan" else True))
    except:
        await callback.message.delete()
        await callback.message.answer(
            "🎭 Выберите формат отображения коллекции" if dat != "chan" else "🧳 Выберите формат отображения коллекции",
            reply_markup=InlineButtons.collection_kb(False if dat != "chan" else True))


@dp.callback_query(F.data[:9] == "rare_mode")
async def rare_mode_my_collection(callback: types.CallbackQuery, state: FSMContext):
    cards = await search_user_cards(callback.from_user.id, "Up")
    trade_status = callback.data.split(":")[-1]

    buttons = []

    used = []
    for card in cards:

        if card.rareness == 0 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Обычные",
                            "callback_data": "rare_by_0:0" if trade_status == "None" else "chan_rare_by_0:0"})

        elif card.rareness == 5 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Редкие",
                            "callback_data": "rare_by_0:5" if trade_status == "None" else "chan_rare_by_0:5"})

        elif card.rareness == 1 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Необычные",
                            "callback_data": "rare_by_0:1" if trade_status == "None" else "chan_rare_by_0:1"})

        elif card.rareness == 2 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Эпические",
                            "callback_data": "rare_by_0:2" if trade_status == "None" else "chan_rare_by_0:2"})

        elif card.rareness == 3 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Уникальные",
                            "callback_data": "rare_by_0:3" if trade_status == "None" else "chan_rare_by_0:3"})

        elif card.rareness == 4 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Легендарные",
                            "callback_data": "rare_by_0:4" if trade_status == "None" else "chan_rare_by_0:4"})

        elif card.rareness == 6 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Эксклюзивные",
                            "callback_data": "rare_by_0:6" if trade_status == "None" else "chan_rare_by_0:6"})

        elif card.rareness == 7 and card.rareness not in used:
            used.append(card.rareness)
            buttons.append({"text": "Мифические",
                            "callback_data": "rare_by_0:7" if trade_status == "None" else "chan_rare_by_0:7"})

    await callback.message.edit_text("Выберите редкость карт", reply_markup=InlineButtons.rare_mode_kb(buttons))


@dp.callback_query(F.data[:8] == "rare_by_")
async def rare_sort(callback: types.CallbackQuery, state: FSMContext):
    rarity = int(callback.data.split(":")[-1])
    card_list = await search_user_cards(callback.from_user.id, None, rarity)
    card_num = len(card_list)

    tasks = []
    add_data = {}

    num = int(callback.data.split(":")[0].replace("rare_by_", ""))

    add_data['<<<'] = f"rare_by_0:{rarity}"
    add_data['<<'] = "rare_by_" + str(num - 1) + ":" + str(rarity)
    add_data['>>'] = "rare_by_" + str(num + 1) + ":" + str(rarity)
    add_data['>>>'] = f"rare_by_{len(card_list) - 1}" + ":" + str(rarity)

    add_data['num1_text'] = '(' + str(num + 1) + '/' + str(card_num) + ')'
    add_data['num1_data'] = "..."

    rareness = get_rareness_by_num(rarity)

    caption_str = str(card_list[num].player_name) + " *" + str(card_list[num].player_nickname) \
                  + "*\nРейтинг: " + "*" + str(card_list[num].points) \
                  + "*\nРедкость: " + "*" + rareness \
                  + "*\nКоманда: " + "*" + str(card_list[num].team) + "*\n"

    if len(card_list) == 1:
        tasks.append("num1")
        tasks.append("num1_not_chan")

        # print(tasks, add_data)

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == 0:

        tasks.append("num0")
        tasks.append("num0_not_chan")

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == len(card_list) - 1:
        tasks.append("num_len-1")
        tasks.append("num_len-1_not_chan")

    else:
        tasks.append("num_else")
        tasks.append("num_else_not_chan")

    await callback.message.edit_media(caption=caption_str,
                                      media=InputMediaPhoto(media=str(card_list[num].photo_id), caption=caption_str,
                                                            parse_mode='Markdown'),
                                      reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data))


@dp.callback_query(F.data[:13] == "chan_rare_by_")
async def rare_sort_1(callback: types.CallbackQuery, state: FSMContext):
    rarity = int(callback.data.split(":")[-1])
    card_list = await search_user_cards(callback.from_user.id, None, rarity)
    card_num = len(card_list)

    tasks = []
    add_data = {}

    num = int(callback.data.split(":")[0].replace("chan_rare_by_", ""))

    tasks.append("Выбрать для обмена")
    add_data['Выбрать для обмена'] = "offer_" + str(card_list[num].card_id)

    add_data['<<<'] = f"chan_rare_by_0:{rarity}"
    add_data['<<'] = "chan_rare_by_" + str(num - 1) + ":" + str(rarity)
    add_data['>>'] = "chan_rare_by_" + str(num + 1) + ":" + str(rarity)
    add_data['>>>'] = f"chan_rare_by_{len(card_list) - 1}" + ":" + str(rarity)

    add_data['num1_text'] = '(' + str(num + 1) + '/' + str(card_num) + ')'
    add_data['num1_data'] = "..."

    rareness = get_rareness_by_num(rarity)

    caption_str = str(card_list[num].player_name) + " *" + str(card_list[num].player_nickname) \
                  + "*\nРейтинг: " + "*" + str(card_list[num].points) \
                  + "*\nРедкость: " + "*" + rareness \
                  + "*\nКоманда: " + "*" + str(card_list[num].team) + "*\n"

    if len(card_list) == 1:
        tasks.append("num1")
        tasks.append("num1_chan")

        # print(tasks, add_data)

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == 0:

        tasks.append("num0")
        tasks.append("num0_chan")

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == len(card_list) - 1:
        tasks.append("num_len-1")
        tasks.append("num_len-1_chan")

    else:
        tasks.append("num_else")
        tasks.append("num_else_chan")

    await callback.message.edit_media(caption=caption_str,
                                      media=InputMediaPhoto(media=str(card_list[num].photo_id), caption=caption_str,
                                                            parse_mode='Markdown'),
                                      reply_markup=InlineButtons.show_card_by_rare_kb(tasks, add_data))


@dp.callback_query(Has_One_Chan_Filter())
async def show_card_one_by_one(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        sorting = data['sorting']
    except:
        # traceback.print_exc()
        sorting = None

    local_sort = 22

    if "sort_rate" in callback.data:
        match sorting:

            case "Down":
                local_sort = "Up"
            case "Up":
                local_sort = None
            case None:
                local_sort = "Down"

    # print(sorting, local_sort)

    card_list = await search_user_cards(callback.from_user.id, sorting if local_sort == 22 else local_sort)

    if len(card_list) == 0:
        await callback.message.edit_text(text="Ваша коллекция карточек сейчас пуста",
                                         reply_markup=InlineButtons.take_card_kb())
        return

    tasks = []
    add_data = {}

    match sorting:

        case "Down":
            if local_sort == 22:
                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ⬇️",
                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Up")


            else:

                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ⬆️",

                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Up")

        case "Up":

            if local_sort == 22:
                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ⬆️",
                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting=None)
            else:

                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ❌",

                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting=None)

        case None:

            if local_sort == 22:
                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ❌",
                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Down")

            else:
                tasks.append("sort_button")
                add_data["sort_button"] = {"text": "️Рейтинг ⬇️",
                                           "callback_data": "{}:sort_rate".format(
                                               "one_by_0" if "one_" in callback.data else "chan_by_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Down")

    if callback.data.split("_")[0] != "chan":
        num = int(callback.data.split(":")[0].replace("one_by_", ""))

    else:
        num = int(callback.data.split(":")[0].replace("chan_by_", ""))

    card_num = (await search_user_in_db(callback.from_user.id)).card_num

    if callback.data.split("_")[0] != "chan":

        add_data['<<<'] = "one_by_0"
        add_data['<<'] = "one_by_" + str(num - 1)
        add_data['>>'] = "one_by_" + str(num + 1)
        add_data['>>>'] = f"one_by_{len(card_list) - 1}"

    else:
        tasks.append("Выбрать для обмена")
        add_data['Выбрать для обмена'] = "offer_" + str(card_list[num].card_id)
        add_data['<<<'] = "chan_by_0"
        add_data['<<'] = "chan_by_" + str(num - 1)
        add_data['>>'] = "chan_by_" + str(num + 1)
        add_data['>>>'] = f"chan_by_{len(card_list) - 1}"

    add_data['num1_text'] = '(' + str(num + 1) + '/' + str(card_num) + ')'
    add_data['num1_data'] = "..."

    rareness = get_rareness_by_num(card_list[num].rareness)

    caption_str = str(card_list[num].player_name) + " *" + str(card_list[num].player_nickname) \
                  + "*\nРейтинг: " + "*" + str(card_list[num].points) + "*" \
                  + "\nРедкость: " + "*" + rareness + "*" \
                  + "\nКоманда: " + "*" + str(card_list[num].team) + "*\n"

    if len(card_list) == 1:
        tasks.append("num1")

        if callback.data.split("_")[0] != "chan":
            tasks.append("num1_not_chan")
        else:
            tasks.append("num1_chan")

        # print(tasks, add_data)

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_one_by_one_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == 0:

        tasks.append("num0")
        if callback.data.split("_")[0] != "chan":
            tasks.append("num0_not_chan")
        else:
            tasks.append("num0_chan")

        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id, card_list[num].photo_id,
                                       reply_markup=InlineButtons.show_card_one_by_one_kb(tasks, add_data),
                                       caption=caption_str, parse_mode='Markdown')

            return

    elif num == len(card_list) - 1:
        tasks.append("num_len-1")
        if callback.data.split("_")[0] != "chan":
            tasks.append("num_len-1_not_chan")
        else:
            tasks.append("num_len-1_chan")

    else:
        tasks.append("num_else")
        if callback.data.split("_")[0] != "chan":
            tasks.append("num_else_not_chan")
        else:
            tasks.append("num_else_chan")

    await callback.message.edit_media(
        media=InputMediaPhoto(media=str(card_list[num].photo_id), caption=caption_str, parse_mode='Markdown'),
        reply_markup=InlineButtons.show_card_one_by_one_kb(tasks, add_data))


@dp.callback_query(F.data[:6] == "offer_")
async def insert_card_to_offer(callback: types.CallbackQuery, state: FSMContext):
    card_id = int(callback.data.replace("offer_", ""))

    bool_pl = await second_user_had_card(callback.from_user.id)

    if not await is_offer_defined(callback.from_user.id):
        # bot.clear_step_handler_by_chat_id(callback.from_user.id)

        await create_new_change_offer(callback.from_user.id, card_id)

        await callback.message.answer("Напишите юзернейм пользователя (@username), с которым хотите обменяться")
        await state.set_state(UserState.get_second_user_for_offer.state)


    elif bool_pl != -1 and not bool_pl:
        await add_card_to_offer(callback.from_user.id, card_id)

        await callback.message.delete()
        msg = await callback.message.answer("✅ Предложение обмена успешно отправлено, ожидайте")

        user_id = await get_first_user(callback.from_user.id)
        card = await get_trade_card(user_id, 1)
        card1 = await get_trade_card(user_id, 0)

        await bot.send_photo(chat_id=user_id, photo=card.photo_id,
                             caption="✅ Пользователь ответил на ваше предложение обмена!\n"
                                     "Вы получите эту карточку за вашу:\n" + card1.player_name + " aka " + card1.player_nickname + "\n" +
                                     "С редкостью - " + get_rareness_by_num(card1.rareness),
                             reply_markup=InlineButtons.insert_card_to_offer_kb())


# функция игры в пенальти
@dp.callback_query(F.data[:4] == "pen_")
async def penalti_game(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "pen_canc":
        await bot.answer_callback_query(callback.id)

        res = await delete_game(callback.from_user.id)
        msg = await callback.message.edit_text("❌ Вы отклонили игру в пенальти",
                                               reply_markup=InlineButtons.pen_canc_kb())

        msg = await bot.send_message(chat_id=res[0],
                                     text=f"❌ @{await get_username_by_id(res[1])} отклонил предложение игры",
                                     reply_markup=InlineButtons.pen_canc_kb())

        return

    if callback.data == "pen_start":
        await callback.message.delete()
        await bot.answer_callback_query(callback.id)

        await start_game(callback.from_user.id)
        kicker_id = await get_kicker(callback.from_user.id)

        print(kicker_id)

        # await bot.send_message("До")

        await bot.send_photo(chat_id=callback.from_user.id, photo=FSInputFile('images/keeper.png'),
                             caption="Выбери сторону куда ты хочешь прыгнуть",
                             reply_markup=InlineButtons.pen_start_kb())

        await bot.send_photo(chat_id=kicker_id, photo=FSInputFile('images/keeper.png'),
                             caption="Выбери угол, в который хочешь ударить",
                             reply_markup=InlineButtons.pen_start_kb())
    else:

        await callback.message.edit_reply_markup(reply_markup=None)
        # print(callback.data)


        res = await check_def_and_kicker_status(callback.from_user.id)

        if not res[1] and not res[0]: # not (await kicker_status(callback.from_user.id)) and not (await check_def_status(callback.from_user.id)):

            await callback.message.edit_reply_markup(reply_markup=InlineButtons.pen_else_kb())
            await callback.answer("Твой соперник еще не сделал удар.", show_alert=True)

        elif not res[1] and res[0]: # (await check_def_status(callback.from_user.id)) and not (await kicker_status(callback.from_user.id)):

            num = callback.data.replace("pen_", "")

            await place_turn_in_db(callback.from_user.id, num)
            await change_kicker(callback.from_user.id)

            res = await is_scored(callback.from_user.id)

            scores = await get_score_str(callback.from_user.id)
            # print(scores)

            keeper_text = None

            if res[0]:
                kicker_text = f"⚽️ ГОЛ!!!\n@{await get_username_by_id(res[1])} прыгнул в другую сторону\n" \
                              f"Результаты твоих ударов:\n{scores[0]}\n" \
                              f"Результаты ударов противника:\n{scores[1]}"
                keeper_text = f"❌ Ты пропустил гол\n@{await get_username_by_id(res[2])} бил в другой угол\n" \
                              f"Результаты твоих ударов:\n{scores[1]}\n" \
                              f"Результаты ударов противника:\n{scores[0]}"
            elif res[1] != -1:
                kicker_text = f"❌ Увы ты не забил\n@{await get_username_by_id(res[1])} угадал твой удар\n" \
                              f"Результаты твоих ударов:\n{scores[0]}\n" \
                              f"Результаты ударов противника:\n{scores[1]}"
                keeper_text = f"🏆 Ты отбил удар\n@{await get_username_by_id(res[2])} бил в тот же угол\n" \
                              f"Результаты твоих ударов:\n{scores[1]}\n" \
                              f"Результаты ударов противника:\n{scores[0]}"

            scores = [scores[0].replace("\U0000231B", ""), scores[1].replace("\U0000231B", "")]
            finish = await check_finish_game_penalti(callback, res, scores)

            try:
                keeper_id = res[1]
                kicker_id = res[2]
            except:
                print("Ошибка")


            if not finish:
                try:
                    await bot.send_message(kicker_id, kicker_text)

                except UnboundLocalError as err:

                    print("Ссылка на переменную происходит раньше ее определения")
                    print(err)

                if keeper_text:
                    await callback.message.edit_caption(caption=f"Ваш выбор - {num}", reply_markup=None)
                    await bot.send_message(keeper_id, keeper_text)
                    # await change_kicker(res[2])
                    await bot.send_photo(kicker_id, FSInputFile('images/keeper.png'),
                                         caption="Выбери угол, в который хочешь прыгнуть",
                                         reply_markup=InlineButtons.pen_else_kb())
                    await bot.send_photo(keeper_id, FSInputFile('images/keeper.png'),
                                         caption="Выбери угол, в который хочешь ударить",
                                         reply_markup=InlineButtons.pen_else_kb())
                    return

            else:

                await callback.message.edit_caption(caption=f"Ваш выбор - {num}", reply_markup=None)
                # print("change")
                # await change_def_status(callback.from_user.id)



        # elif not (await kicker_status(callback.from_user.id)):
        #     #             print("asdasdww")
        #     await callback.answer("Твой соперник еще не сделал удар.", show_alert=True)

        else:

            await set_kick_time(callback.from_user.id)
            num = callback.data.replace("pen_", "")
            await callback.message.edit_caption(caption=f"Ваш выбор - {num}\nОжидайте хода второго игрока",
                                                reply_markup=None)
            # print(num)

            await place_turn_in_db(callback.from_user.id, num)
            print(f"Turn {callback.from_user.id}")

            res = await is_scored(callback.from_user.id)
            print(f"is scored {callback.from_user.id}")
            scores = await get_score_str(callback.from_user.id)
            #             print(scores)

            keeper_text = None

            if res[0]:
                kicker_text = f"⚽️ ГОЛ!!!\n@{await get_username_by_id(res[1])} прыгнул в другую сторону\n" \
                              f"Результаты твоих ударов:\n{scores[0]}\n" \
                              f"Результаты ударов противника:\n{scores[1]}"
                keeper_text = f"❌ Ты пропустил гол\n@{await get_username_by_id(res[2])} бил в другой угол\n" \
                              f"Результаты твоих ударов:\n{scores[1]}\n" \
                              f"Результаты ударов противника:\n{scores[0]}"
            elif res[1] != -1:
                kicker_text = f"❌ Увы ты не забил\n@{await get_username_by_id(res[1])} угадал твой удар\n" \
                              f"Результаты твоих ударов:\n{scores[0]}\n" \
                              f"Результаты ударов противника:\n{scores[1]}"
                keeper_text = f"🏆 Ты отбил удар\n@{await get_username_by_id(res[2])} бил в тот же угол\n" \
                              f"Результаты твоих ударов:\n{scores[1]}\n" \
                              f"Результаты ударов противника:\n{scores[0]}"

            scores = [scores[0].replace("\U0000231B", ""), scores[1].replace("\U0000231B", "")]
            finish = await check_finish_game_penalti(callback, res, scores)
            if not finish:
                try:
                    await bot.send_message(res[1], kicker_text)

                except UnboundLocalError as err:

                    print("Ссылка на переменную происходит раньше ее определения")
                    print(err)

                if keeper_text:
                    await bot.send_message(res[2], keeper_text)
                    await change_kicker(res[2])
                    await bot.send_photo(res[1], FSInputFile('images/keeper.png'),
                                         caption="Выбери угол, в который хочешь прыгнуть",
                                         reply_markup=InlineButtons.pen_else_kb())
                    await bot.send_photo(res[2], FSInputFile('images/keeper.png'),
                                         caption="Выбери угол, в который хочешь ударить",
                                         reply_markup=InlineButtons.pen_else_kb())
                    return

                # print("change")
                await change_def_status(callback.from_user.id)

            else:

                await callback.message.edit_caption(caption=f"Ваш выбор - {num}", reply_markup=None)


# функция завершения игры в самом боте для упрощения синтаксиса
async def check_finish_game_penalti(callback: types.CallbackQuery, res: list, scores: list):
    finished = await is_finished(callback.from_user.id)
    # обработка ошибок
    if finished == -1:
        error_str = "Во время игры возникла ошибка, сеанс был завершен"
        msg = await bot.send_message(chat_id=callback.from_user.id,
                                     text=error_str, reply_markup=InlineButtons.pen_canc_kb())
        msg = await bot.send_message(chat_id=await get_second_user(callback.from_user.id), text=error_str,
                                     reply_markup=InlineButtons.pen_canc_kb())
        await delete_game(callback.from_user.id)
        return True
    # обработка успешного завершения игры
    if finished:
        game_res = await finish_game(callback.from_user.id)
        if game_res[0] == 0:

            draw_str = f"Результаты ударов @{await get_username_by_id(res[2])}:\n{scores[0]}\n" \
                       f"Результаты ударов @{await get_username_by_id(res[1])}:\n{scores[1]}\n" \
                       f"🏆 Вы забили одинаковое количество голов! " \
                       f"Предлагаем вам переигровку или же ничью, выбор за вами!"

            msg = await bot.send_message(res[1], text=draw_str, reply_markup=InlineButtons.pen_finished_0_kb())
            msg = await bot.send_message(res[2], text=draw_str, reply_markup=InlineButtons.pen_finished_0_kb())

        else:

            fin_str = f"Результаты ударов @{await get_username_by_id(res[2])}:\n{scores[0]}\n" \
                      f"Результаты ударов @{await get_username_by_id(res[1])}:\n{scores[1]}\n" \
                      f"Победитель - @{await get_username_by_id(game_res[1])}"
            msg = await bot.send_message(
                game_res[2], text=fin_str, reply_markup=InlineButtons.pen_finished_1_kb())
            msg = await bot.send_message(
                game_res[1], text=fin_str, reply_markup=InlineButtons.pen_finished_1_kb())

        await delete_game(callback.from_user.id)
        return True
    return False


@dp.callback_query(F.data[:5] == "trade")
async def call_trade(callback: types.CallbackQuery):
    if callback.data == "trade_canc":
        trade_id = await cancel_trade(callback.from_user.id)

        if trade_id[0] == 0:
            await callback.message.delete()
            msg = await bot.send_message(callback.from_user.id,
                                         "❌ Вы отменили обмен!", reply_markup=InlineButtons.call_trade_kb())

            if trade_id[1] != 0:
                msg = await bot.send_message(trade_id[1], "❌ Обмен был отклонён",
                                             reply_markup=InlineButtons.call_trade_kb())
            return

        if trade_id[0] != callback.from_user.id:
            await callback.message.delete()
            msg = await bot.send_message(trade_id[0], "❌ Увы, сделка сорвалась.",
                                         reply_markup=InlineButtons.call_trade_kb())
            msg1 = await bot.send_message(
                trade_id[1], "❌ Вы отменили обмен!", reply_markup=InlineButtons.call_trade_kb())
        else:
            await callback.message.delete()
            msg = await bot.send_message(
                chat_id=trade_id[1], text="❌ Увы, сделка сорвалась.", reply_markup=InlineButtons.call_trade_kb())
            msg1 = await bot.send_message(
                trade_id[0], "❌ Вы отменили обмен!", reply_markup=InlineButtons.call_trade_kb())


    if callback.data == "trade":
        await callback.message.delete()
        trade_id = await do_trade(callback.from_user.id)

        if trade_id[0] != callback.from_user.id:
            msg = await bot.send_message(trade_id[0], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                         reply_markup=InlineButtons.call_trade_kb())
            msg1 = await bot.send_message(trade_id[1], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                          reply_markup=InlineButtons.call_trade_kb())
        else:
            msg = await bot.send_message(trade_id[1], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                         reply_markup=InlineButtons.call_trade_kb())
            msg1 = await bot.send_message(trade_id[0], "✅ Cделка прошла успешно!\nВремя проверить коллекцию",
                                          reply_markup=InlineButtons.call_trade_kb())


# обработка платежа пользователя
@dp.callback_query(Get_Buy_Message_Filter())
async def get_buy_message(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "0":
        await check_pay(callback, state)

    else:
        await clear_user_transaction(callback.from_user.id)
        operation_id = str(uuid.uuid4())
        redirect_uri = await quick_pay("buy cards", await get_price(int(callback.data)), operation_id)

        if int(callback.data) != 4:
            await place_operation_in_db(
                callback.from_user.id, operation_id, callback.data)
        else:
            await place_operation_in_db(
                callback.from_user.id, operation_id, callback.data)

        await callback.message.edit_text("Ваш заказ сформирован\nОплатите его по кнопке ниже",
                                         reply_markup=InlineButtons.get_buy_message_kb(redirect_uri))


@dp.callback_query(F.data == "check_pay")
async def check_pay(callback: types.CallbackQuery, state: FSMContext):
    free_card = await check_free_card(callback.from_user.id)

    print([callback.data, free_card])

    if callback.data == "0" and free_card[0]:

        await callback.message.delete()

        random_card = await get_random_card(1, "random_card")

        await add_cards_to_user(random_card, callback.from_user.id)
        await push_free_card_date(callback.from_user.id)

        await set_get_msg(callback.from_user.id, 0)
        await get_new_cards(callback, state)

    elif callback.data == "0" and not free_card[0]:

        await callback.message.delete()

        ans = free_card[1].split(":")
        # изменена одна строчка ниже
        ans_str = ans[0] + "ч " + ans[1] + "мин ⏱️"

        await callback.message.answer("Ты недавно получал свою бесплатную карточку! "
                                      "Следующую ты можешь получить через " + ans_str + ". "
                                                                                        "Если не хочешь ждать - приобретай дополнительные карточки!",
                                      reply_markup=InlineButtons.card_shop_kb())

    elif callback.data != "0":

        print(callback.data)
        operation = await get_active_transaction(callback.from_user.id)
        operation_id = operation.operation_id
        if await check_payment(operation_id):

            await callback.message.delete()

            # добавлена одна строчка кода ниже
            await save_transaction(callback.from_user.id)
            product_id = int(operation.operation_name)
            if int(product_id) == 1:
                card_num = 1
            if int(product_id) == 2:
                card_num = 3
            if int(product_id) == 3:
                card_num = 5
            if int(product_id) == 4:
                await update_user_strikes(callback.from_user.id, 1)

                await callback.message.answer("Успешно ✅, купленные удары уже начисленны вам,"
                                              "время проверить удачу!", reply_markup=InlineButtons.mini_games_kb())
                return

            await add_cards_to_user((await get_random_card(card_num, "random_card")), callback.from_user.id)

            await plus_user_transactions(callback.from_user.id)

            await callback.message.answer("Успешно ✅, получите ваш заказ", reply_markup=InlineButtons.get_cards_kb())

        else:

            await bot.answer_callback_query(callback.id)

            # await callback.message.answer("Успешно ✅, получите ваш заказ", reply_markup=InlineButtons.get_cards_kb())


# демонстрация новых карточек, которые получил пользователь
# в процессе открытия набора
@dp.callback_query(F.data == "get_new_cards")
async def get_new_cards(callback: types.CallbackQuery, state: FSMContext):

    card_info = await get_last_cards(callback.from_user.id)
    # print(card_info)
    if card_info[1] >= 1:
        rare = get_rareness_by_num(card_info[0][0].rareness)

        ans = str(card_info[0][0].player_name) + " aka " + str(card_info[0][0].player_nickname) \
              + "\nРейтинг: " + "*" + str(card_info[0][0].points) + "*" \
              + "\nРедкость: " + "*" + rare + "*" \
              + "\nКоманда: " + "*" + str(card_info[0][0].team) + "*" + "\n"

        cards_len = len(card_info[0])
        add_data = {}

        if card_info[1] == 1:
            markup = InlineButtons.show_new_card_kb(True)
        else:

            add_data['format'] = "first"  # ... | last
            add_data['card_number'] = 1
            add_data['cards'] = cards_len

            markup = InlineButtons.show_new_card_kb(False, add_data)
            await state.update_data(cards=card_info[0],
                                    card_number=0)

        await bot.answer_callback_query(callback.id)

        try:
            await callback.message.delete()
        except:
            pass

        await bot.send_photo(callback.from_user.id, card_info[0][0].photo_id, caption=ans, parse_mode="Markdown",
                             reply_markup=markup)

    else:



        await return_to_lk(callback, state)

        # await callback.message.edit_text( text="У вас нет доступных к открытию карточек", reply_markup=InlineButtons.get_second_user_for_offer_kb())


@dp.callback_query(F.data[:18] == "slide_bought_cards")
async def slide_bought_cards(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    action = callback.data.split(":")[-1]
    add_data = {}

    cards = data['cards']

    if action == "first":
        card_number = 0
        await state.update_data(card_number=0)

        add_data['format'] = "first"
        add_data['card_number'] = card_number + 1
        add_data['cards'] = len(cards)

        markup = InlineButtons.show_new_card_kb(False, add_data)

    elif action == "nothing":
        await bot.answer_callback_query(callback.id)
        return

    elif action == "next":
        card_number = data['card_number'] + 1
        await state.update_data(card_number=card_number)

        if card_number + 1 == len(cards):
            add_data['format'] = "last"
        else:
            add_data['format'] = "..."
        add_data['card_number'] = card_number + 1
        add_data['cards'] = len(cards)

        markup = InlineButtons.show_new_card_kb(False, add_data)

    elif action == "previous":
        card_number = data['card_number'] - 1
        await state.update_data(card_number=card_number)

        if card_number == 0:
            add_data['format'] = "first"
        else:
            add_data['format'] = "..."

        add_data['card_number'] = card_number + 1
        add_data['cards'] = len(cards)

        markup = InlineButtons.show_new_card_kb(False, add_data)

    elif action == "last":
        card_number = len(cards) - 1

        await state.update_data(card_number=len(cards) - 1)

        add_data['format'] = "last"
        add_data['card_number'] = len(cards)
        add_data['cards'] = len(cards)

        markup = InlineButtons.show_new_card_kb(False, add_data)

    print(card_number)

    rare = get_rareness_by_num(cards[card_number].rareness)

    ans = str(cards[card_number].player_name) + " aka " + str(cards[card_number].player_nickname) \
          + "\nРейтинг: " + "*" + str(cards[card_number].points) + "*" \
          + "\nРедкость: " + "*" + rare + "*" \
          + "\nКоманда: " + "*" + str(cards[card_number].team) + "*" + "\n"

    await callback.message.edit_media(
        media=InputMediaPhoto(media=str(cards[card_number].photo_id), caption=ans, parse_mode='Markdown'),
        reply_markup=markup)


@dp.callback_query(F.data == "admin")
async def get_admin(callback: types.CallbackQuery):
    # bot.clear_step_handler_by_chat_id(callback.from_user.id)

    try:
        await callback.message.edit_text("Добро пожаловать в админскую панель\n"
                                         "Выберете раздел с которым вы хотите работать",
                                         reply_markup=AdminInlineKeyboard.get_admin_kb())
    except:
        await callback.message.delete()
        await callback.message.answer("Добро пожаловать в админскую панель\n"
                                      "Выберете раздел с которым вы хотите работать",
                                      reply_markup=AdminInlineKeyboard.get_admin_kb())


@dp.callback_query(F.data[:6] == "admin_")
async def admin_sections(callback: types.CallbackQuery):
    # bot.clear_step_handler_by_chat_id(callback.from_user.id)

    section = callback.data.split("_")[1]

    tasks = []
    add_data = {}

    if section != "users":

        add_data['section'] = section
        tasks.append("not_section")

        if section == "card":
            tasks.append("card")
            await callback.message.edit_text("Вы находитесь в разделе управления карточками!\n"
                                             "Выберете действие, которое хотите выполнить",
                                             reply_markup=AdminInlineKeyboard.admin_sections_kb(tasks, add_data))
        else:
            tasks.append("not_card")
            await callback.message.edit_text("Вы находитесь в разделе управления промокодами!\n"
                                             "Выберете действие, которое хотите выполнить",
                                             reply_markup=AdminInlineKeyboard.admin_sections_kb(tasks, add_data))
    else:
        tasks.append("section")
        await callback.message.edit_text("Вы находитесь в разделе управления пользователями!\n"
                                         "Выберете действие, которое хотите выбрать",
                                         reply_markup=AdminInlineKeyboard.admin_sections_kb(tasks, add_data))


@dp.callback_query(F.data[:8] == "get_user")
async def users_processing(callback: types.CallbackQuery, state: FSMContext):
    # bot.clear_step_handler_by_chat_id(callback.from_user.id)

    if callback.data == "get_user":
        await callback.message.edit_text("Напишите @username пользователя, "
                                         "о котором хотите получить информацию",
                                         reply_markup=AdminInlineKeyboard.users_processing_kb())
        await state.set_state(UserState.get_username_for_admin.state)
        return
    if "get_user_hist" in callback.data:
        user_id = int(callback.data.split("_")[3])
        ans_str = await get_user_transactions_info(
            user_id, await get_username_by_id(user_id))
        await callback.message.edit_text(text=ans_str, reply_markup=AdminInlineKeyboard.users_processing_kb())


@dp.callback_query(Redact_Card_Filter())
async def redact_card(callback: types.CallbackQuery, state: FSMContext):
    # bot.clear_step_handler_by_chat_id(callback.from_user.id)

    msg_id = callback.message.message_id
    card = (await get_card_by_id(int(callback.data.split("_")[0])))[0]
    new_caption = card + \
                  "\n\nОтправьте новые характеристики игрока в формате\n" \
                  "1.Имя игрока\n2.Никнейм игрока\n3.Команда игрока\n4.Редкость карточки\n" \
                  "5.Рейтинг карточки\n\nцифры указывать не надо"
    if callback.message.caption:
        new_caption = callback.message.caption + "\n\nОтправьте новые характеристики игрока в формате\n" \
                                                 "1.Имя игрока\n2.Никнейм игрока\n3.Команда игрока\n4.Редкость карточки\n" \
                                                 "5.Рейтинг карточки\n\nцифры указывать не надо"
    await bot.edit_message_caption(chat_id=callback.from_user.id, message_id=msg_id, caption=new_caption)

    await state.update_data(card_id=int(callback.data.split("_")[0]))
    await state.set_state(UserState.get_new_photo.state)


@dp.callback_query(F.data[-4:] == "_new")
async def _new(callback: types.CallbackQuery, state: FSMContext):
    card_id = callback.data.split("_")[0]

    await delete_card_(int(card_id))

    try:
        await callback.message.edit_text(text="Заного впишите характеристики карточки в таком формате:"
                                              "1.Имя игрока\n"
                                              "2.Никнейм игрока\n"
                                              "3.Команда игрока\n"
                                              "4.Редкость карточки\n"
                                              "5.Рейтинг карточки\n\n"
                                              "цифры указывать не надо",
                                         reply_markup=AdminInlineKeyboard.adm_add_card_kb())
    except:
        await callback.message.delete()
        await callback.message.answer(text="Заного впишите характеристики карточки в таком формате:"
                                           "1.Имя игрока\n"
                                           "2.Никнейм игрока\n"
                                           "3.Команда игрока\n"
                                           "4.Редкость карточки\n"
                                           "5.Рейтинг карточки\n\n"
                                           "цифры указывать не надо",
                                      reply_markup=AdminInlineKeyboard.adm_add_card_kb())


@dp.callback_query(F.data[:4] == "adm_")
async def admin_execute(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return

    if callback.data == "adm_add_card":
        # bot.clear_step_handler_by_chat_id(callback.from_user.id)

        await callback.message.edit_text(text="Для начала укажите характеристики карточки в формате\n"
                                              "1.Имя игрока\n"
                                              "2.Никнейм игрока\n"
                                              "3.Команда игрока\n"
                                              "4.Редкость карточки\n"
                                              "5.Рейтинг карточки\n\n"
                                              "цифры указывать не надо",
                                         reply_markup=AdminInlineKeyboard.adm_add_card_kb())

        await state.set_state(UserState.get_photo.state)
    if callback.data == "adm_add_promo":
        # bot.clear_step_handler_by_chat_id(callback.from_user.id)

        # были изменены аргументы этой вызываемой функции
        await callback.message.edit_text("Напишите промокод, который хотите добавить"
                                         "\nЧтобы указать количество использований "
                                         "напишите это число через пробел от промокода",
                                         reply_markup=AdminInlineKeyboard.adm_add_card_kb())
        await state.set_state(UserState.get_promo_text.state)

    if callback.data == "adm_del_promo":

        promos = await select_all_promos()

        promos_for_kb = []

        # print(promos)
        if promos != None:
            for i in range(0, len(promos[0])):
                promos_for_kb.append({"text": str(promos[0][i].promo) + " - " + str(promos[1][i].card_id),
                                      "callback_data": "promo_" + str(promos[0][i].promo_id) + "_del"})
            # изменена строчка кода ниже (убран таб)

        else:

            msg = await callback.message.edit_text(text="Сейчас нет активных промокодов",
                                                   reply_markup=AdminInlineKeyboard.adm_update_kb())

            return
        await callback.message.edit_text(
            "Выберете промокод для удаления\nВсе промокоды указаны в формате промокод - карточка",
            reply_markup=AdminInlineKeyboard.adm_del_promo_kb(promos_for_kb))
    # исправлен код функции ниже
    if callback.data == "adm_update":
        await callback.message.edit_text(text="Тут можно выбрать карточку для редактирования, "
                                              "чтобы открыть просмотр нажмите на кнопку",
                                         reply_markup=AdminInlineKeyboard.adm_update_kb())
    if callback.data == "adm_del_card":
        await callback.message.edit_text("Тут можно выбрать карточку для удаления, "
                                         "чтобы открыть нажмите на кнопку",
                                         reply_markup=AdminInlineKeyboard.adm_del_card_kb())


@dp.callback_query(Show_All_Cards_Filter())
async def show_all_cards(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        sorting = data['sorting']
    except:
        # traceback.print_exc()
        sorting = None

    local_sort = 22

    if "sort_rate" in callback.data:
        match sorting:

            case "Down":
                local_sort = "Up"
            case "Up":
                local_sort = None
            case None:
                local_sort = "Down"

    tasks = []
    buttons = {}

    match sorting:

        case "Down":
            if local_sort == 22:
                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ⬇️",
                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Up")


            else:

                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ⬆️",

                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Up")

        case "Up":

            if local_sort == 22:
                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ⬆️",
                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting=None)
            else:

                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ❌",

                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting=None)

        case None:

            if local_sort == 22:
                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ❌",
                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Down")

            else:
                tasks.append("sort_button")
                buttons["sort_button"] = {"text": "️Рейтинг ⬇️",
                                          "callback_data": "{}:sort_rate".format(
                                              "redact_62_0" if "redact_" in callback.data else "destroy_62_0" if "destroy_" in callback.data else "choose_0")}

                if "sort_rate" in callback.data:
                    await state.update_data(sorting="Down")

    try:
        num = int(callback.data.split(":")[0].split("_")[2])
    except:
        num = int(callback.data.split(":")[0].split("_")[1])

    card_list = await select_all_cards(sort_mode=sorting if local_sort == 22 else local_sort)

    if "choose_" in callback.data:
        promo_id = int(callback.data.split(":")[0].split("_")[1])

        buttons['choose_btn'] = {"text": "Выбрать в промо",
                                 "callback_data": "promo_" + str(promo_id) + "_" + str(card_list[num].card_id)}
        print(buttons['choose_btn'])
        buttons['back_btn'] = {"text": "<<",
                               "callback_data": "choose_" + str(promo_id) + "_" + str(num - 1)}
        buttons['next_btn'] = {"text": ">>",
                               "callback_data": "choose_" + str(promo_id) + "_" + str(num + 1)}

    if "redact_" in callback.data:
        card_id = 62

        buttons['choose_btn'] = {"text": "Выбрать для редактирования",
                                 "callback_data": str(card_list[num].card_id) + "_old"}
        buttons['back_btn'] = {"text": "<<",
                               "callback_data": "redact_" + str(card_id) + "_" + str(num - 1)}
        buttons['next_btn'] = {"text": ">>",
                               "callback_data": "redact_" + str(card_id) + "_" + str(num + 1)}

    if "destroy_" in callback.data:
        tasks.append("destroy_")
        card_id = 62

        buttons['back_btn'] = {"text": "<<",
                               "callback_data": "destroy_" + str(card_id) + "_" + str(num - 1)}
        buttons['next_btn'] = {"text": ">>",
                               "callback_data": "destroy_" + str(card_id) + "_" + str(num + 1)}

    buttons['num_btn'] = {"text": '(' + str(num + 1) + '/' + str(len(card_list)) + ')',
                          "callback_data": "..."}
    buttons['del_btn'] = {"text": "Удалить",
                          "callback_data": "delete_card_" + str(card_list[num].card_id)}

    if num == 0:
        tasks.append("num_0")
        if callback.message.photo == None:
            await callback.message.delete()
            msg = await bot.send_photo(callback.from_user.id,
                                       card_list[num].photo_id,
                                       reply_markup=AdminInlineKeyboard.show_all_cards_kb(tasks, buttons))

        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=card_list[num].photo_id),
                                              reply_markup=AdminInlineKeyboard.show_all_cards_kb(tasks, buttons))
    elif num == len(card_list) - 1:
        tasks.append("num_len-1")
        await callback.message.edit_media(media=InputMediaPhoto(media=card_list[num].photo_id),
                                          reply_markup=AdminInlineKeyboard.show_all_cards_kb(tasks, buttons))
    else:
        tasks.append("num_else")
        await callback.message.edit_media(media=InputMediaPhoto(media=card_list[num].photo_id),
                                          reply_markup=AdminInlineKeyboard.show_all_cards_kb(tasks, buttons))


# новый хендлер для удаления карточек
@dp.callback_query(F.data[:11] == "delete_card")
async def delete_card(callback: types.CallbackQuery):
    card_id = callback.data.split("_")[2]
    await delete_card_(int(card_id))

    msg = await bot.send_message(callback.from_user.id, "Карточка была успешно удалена",
                                 reply_markup=AdminInlineKeyboard.adm_add_card_kb())



@dp.callback_query(F.data[:6] == "promo_")
async def add_card_to_promo(callback: types.CallbackQuery):
    promo_id = callback.data.split("_")[1]
    if callback.data.split("_")[2] == "del":
        await delete_promo(int(promo_id))

        await callback.message.edit_text("Промокод был успешно удален",
                                         reply_markup=AdminInlineKeyboard.adm_add_card_kb())
        return

    if callback.data.split("_")[2] == "rng":
        await insert_promo_card(int(promo_id), 0)
    else:
        info = callback.data.split("_")
        card_id = info[2]
        await insert_promo_card(int(promo_id), int(card_id))

    await callback.message.delete()
    msg = await bot.send_message(callback.from_user.id, "Промокод был успешно добавлен! Время его проверить",
                                 reply_markup=AdminInlineKeyboard.add_card_to_promo_kb())



@dp.message(F.photo | F.text)
async def check_promocode(message: types.Message, state: FSMContext):
    # print("NOT START")

    await bot.send_message(649811235, f"{message.from_user.id}, Не старт")


    state_ = await state.get_state()

    if state_ == UserState.check_promo.state:

        res = await check_promo_(message.from_user.id, message.text)

        if res[0]:
            # тело этого if было изменено
            if res[1] == 12340000000004321:
                await add_cards_to_user(await get_random_card(1, "random_card"), message.from_user.id)
            else:
                await add_card_to_user_by_card_id(res[1], message.from_user.id)
            await minus_promo_usages(message.text)
            await get_show_new_cards(message)
            # конец изменений
        else:
            msg = await bot.send_message(message.from_user.id,
                                         "Увы, но такого промокода не существует, либо он больше недействительный 😔",
                                         reply_markup=AdminInlineKeyboard.check_promo_kb())


    if state_ == UserState.get_promo_text.state:

        promo = message.text.split(" ")[0]
        if len(message.text.split(" ")) > 1:
            usages = message.text.split(" ")[1]
        else:
            usages = "INF"

        promo_id = await place_promo(promo, usages)
        print(promo_id)

        await message.delete()
        await bot.send_message(message.from_user.id, "Теперь нажмите кнопку выбрать карточку, "
                                                     "чтобы она выдавалась при вводе промокода",
                               reply_markup=AdminInlineKeyboard.get_promo_text_kb(promo_id))

    if state_ == UserState.get_second_user_for_offer.state:

        # bot.clear_step_handler_by_chat_id(message.from_user.id)

        username = message.text.replace("@", "")

        user_id = await get_user_by_username(username)

        if user_id == None:
            await bot.send_message(message.from_user.id,
                                   "Этому пользователю нельзя предложить обмен, попробуйте снова",
                                   reply_markup=InlineButtons.get_second_user_for_offer_kb())
        elif await user_had_offer(user_id):
            await bot.send_message(message.from_user.id,
                                   "Этому пользователю нельзя предложить обмен, так как он учавствует в другом, попробуйте позже",
                                   reply_markup=InlineButtons.get_second_user_for_offer_kb())

        else:
            print(int(message.from_user.id), int(user_id))

            await insert_second_user_(int(message.from_user.id), int(user_id))
            card = await get_trade_card(message.from_user.id, 0)
            msg = await bot.send_message(message.from_user.id, "✅ Предложение обмена успешно отправлено "
                                                               "пользователю - @" + username)


            msg = await bot.send_photo(chat_id=user_id, photo=card.photo_id,
                                       caption="Вам поступило предложение обмена от - @" +
                                               await get_username_by_id(message.from_user.id),
                                       reply_markup=InlineButtons.trade_kb())


    if state_ == UserState.get_username_for_pen.state:

        # изменена одна строчка кода ниже
        tele_id2 = await get_user_by_username(message.text.replace("@", ""))
        if tele_id2 == -1:
            msg = await bot.send_message(message.from_user.id,
                                         "Этому пользователю нельзя предложить игру в Пенальти ☹️\n"
                                         "Ему нужно запустить этого бота и получить свою первую карточку!",
                                         reply_markup=InlineButtons.back_back_kb())

        else:
            # ниже добавлена проверка на разницу в рейтинге
            if await check_delta_rating(message.from_user.id, int(tele_id2)):
                msg = await bot.send_message(message.from_user.id,
                                             "Ты не можешь сыграть в пенальти с " + message.text +
                                             " из-за большой разницы в рейтинге☹️",
                                             reply_markup=InlineButtons.back_back_kb())

                return

            if not await user_in_game(int(tele_id2)):
                await create_game(message.from_user.id)
                await insert_second_user(tele_id2, message.from_user.id)

                msg = await bot.send_message(tele_id2,
                                             "@" + await get_username_by_id(
                                                 message.from_user.id) + " предлагает вам сыграть в Пенальти!",
                                             reply_markup=InlineButtons.user_game_kb(False))

                await bot.send_message(message.from_user.id,
                                       "📩Ваше предложение сыграть в Пенальти было отправлено " + message.text + "!")

                await waiting_user_confirm(message.from_user.id, tele_id2, msg)

            else:

                msg = await bot.send_message(message.from_user.id,
                                             "Этому пользователю нельзя предложить игру в Пенальти ☹️\n"
                                             "Он уже находиться в игре, дождитесь конца или предложите игру кому-нибудь другому",
                                             reply_markup=InlineButtons.user_game_kb(True))


    if state_ == UserState.get_username_for_admin.state:

        user_id = await get_user_by_username(message.text.replace("@", ""))
        if user_id == None:
            await bot.send_message(message.from_user.id, "Пользователь с таким именем не был найден. "
                                                         "Проверьте корректность ввода данных",
                                   reply_markup=AdminInlineKeyboard.users_processing_kb())
        else:

            user_str = await get_user_info(user_id, message.text)
            msg = await bot.send_message(
                message.from_user.id, text=user_str, reply_markup=AdminInlineKeyboard.get_username_for_admin_kb())


    if state_ == UserState.get_photo.state:

        # bot.clear_step_handler_by_chat_id(message.from_user.id)

        player_info = message.text.split("\n")
        print(player_info)
        card = await place_player_in_db(player_info)
        if card != None and check_card_info(player_info) != -1:
            await bot.send_message(message.from_user.id, "Теперь отправьте фото карточки игрока")

            await state.update_data(card_id=card.card_id)
            await state.set_state(UserState.save_card_photo.state)

        else:
            msg = await bot.send_message(message.from_user.id, "Некорректный ввод данных, попробуйте снова",
                                         reply_markup=AdminInlineKeyboard.get_photo_kb())


            await state.set_state(UserState.get_photo.state)

    if state_ == UserState.save_card_photo.state:

        data = await state.get_data()
        card_id = data['card_id']

        if (await set_card_photo(card_id, message.photo[0].file_id)) != -1:

            new_card = await get_card_by_id(card_id)
            await bot.send_photo(message.from_user.id,
                                 new_card[1], caption=new_card[0],
                                 reply_markup=AdminInlineKeyboard.set_card_photo_kb(card_id))
        else:

            msg = await bot.send_message(
                message.from_user.id, "Произошла какая-то ошибка, уже работаем над этим",
                reply_markup=AdminInlineKeyboard.get_photo_kb())


    if state_ == UserState.get_new_photo.state:

        # bot.clear_step_handler_by_chat_id(message.from_user.id)

        data = await state.get_data()
        card_id = data['card_id']

        player_info = message.text.split("\n")

        card = await edit_card_in_db(card_id, player_info)

        if card != None and check_card_info(player_info) != -1:

            msg = await bot.send_message(
                message.from_user.id, "Теперь отправьте фото карточки игрока",
                reply_markup=AdminInlineKeyboard.get_new_photo_kb(False))


            await state.update_data(card_id=card_id)
            await state.set_state(UserState.save_new_card_photo.state)
        else:
            msg = await bot.send_message(message.from_user.id, "Некорректный ввод данных, попробуйте снова",
                                         reply_markup=AdminInlineKeyboard.get_new_photo_kb(False))


            await state.update_data(card_id=card_id)
            await state.set_state(UserState.get_new_photo.state)

    if state_ == UserState.save_new_card_photo.state:

        data = await state.get_data()
        card_id = data['card_id']

        if await set_card_photo(card_id, message.photo[0].file_id) != -1:

            new_card = await get_card_by_id(card_id)
            await bot.send_photo(message.from_user.id,
                                 new_card[1], caption=new_card[0],
                                 reply_markup=AdminInlineKeyboard.save_new_card_photo_kb(True))
            msg = await bot.send_message(message.from_user.id, ".")

        else:

            msg = await bot.send_message(
                message.from_user.id, "Произошла какая-то ошибка, уже работаем над этим",
                reply_markup=AdminInlineKeyboard.save_new_card_photo_kb(False))



async def get_show_new_cards(message: types.Message):
    card_info = await get_last_cards(message.from_user.id)

    if card_info[1] >= 1:
        ans = str(card_info[0][0].player_name) + " " + "*" + str(card_info[0][0].player_nickname) + "*" \
              + "\nРейтинг: " + "*" + str(card_info[0][0].points) + "*" \
              + "\nРедкость: " + "*" + get_rareness_by_num(card_info[0][0].rareness) + "*" \
              + "\nКоманда: " + "*" + str(card_info[0][0].team) + "*" + "\n"

        await bot.send_photo(message.from_user.id, card_info[0][0].photo_id, caption=ans, parse_mode="Markdown",
                             reply_markup=InlineButtons.show_new_card_kb())


async def waiting_user_confirm(user1_id, user2_id, msg):
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
    while datetime.datetime.now() < end_time:

        if await check_confirm_game(user1_id, user2_id):

            break

        else:

            await asyncio.sleep(1)

    else:
        await msg.delete()
        await bot.send_message(chat_id=user1_id, text="К сожалению, ваш оппонент не принял игру за минуту",
                               reply_markup=InlineButtons.back_kb())
        await delete_game(user1_id)


async def search_user_by_username(user_name, tele_id):
    username = user_name.replace("@", "")
    user_list = await select_all_users()
    for user in user_list:
        u = await bot.get_chat_member(CHANNEL_ID, user.tele_id)
        if username == u.user.username and user.tele_id != tele_id:
            return user.tele_id
    return -1


async def time_events_checker():
    while True:
        print("Проверка")
        games_list = await select_all_games()
        if games_list:
            # print(games_list)
            for game in games_list:
                result = await destroy_game(game.user1_id)
                if result[0] != 0:

                    if result[2]:

                        msg = await bot.send_message(result[0],
                                                     "Игрок - @" + await get_username_by_id(
                                                         result[1]) + " слишком долго не отвечал, вы победили!",
                                                     reply_markup=InlineButtons.time_events_checker_kb())

                        msg = await bot.send_message(result[1],
                                                     "Тебя слишком долго не было в игре, поэтому тебе засчитано поражение",
                                                     reply_markup=InlineButtons.time_events_checker_kb())


                    else:
                        msg = await bot.send_message(result[0],
                                                     "Матч признан несостоявшимся из-за длительного ожидания 🏳️",
                                                     reply_markup=InlineButtons.time_events_checker_kb(False))

                        msg = await bot.send_message(result[1],
                                                     "Матч признан несостоявшимся из-за длительного ожидания 🏳️",
                                                     reply_markup=InlineButtons.time_events_checker_kb(False))

        await asyncio.sleep(10)
        # проверка юзеров на возможность получить карточку
        user_list = await get_users_id_for_free_card()

        for user_id in user_list:
            if await is_subscribed(user_id):
                try:
                    msg = await bot.send_message(user_id, "Привет! Ты можешь забрать свою бесплатную карту! 🎁",
                                                 reply_markup=InlineButtons.time_events_checker_2_kb())

                    await set_get_msg(user_id, 1)
                except Exception as e:
                    print(e)
        await unban_users()
        await give_free_strikes()
        await asyncio.sleep(30)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(time_events_checker())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
