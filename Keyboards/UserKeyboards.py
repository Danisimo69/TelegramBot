

import aiogram.types

from Keyboards.InlineConsts import InlineConstructor
from Keyboards.ReplyConsts import DefaultConstructor


class InlineButtons(InlineConstructor):

    @staticmethod
    def start_kb__not_sub() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "Подписаться \U00002705",
                 "url":"https://t.me/offsidecard"}]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def start_kb__sub() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "ℹ Информация",
                 "callback_data": "info"},
                {"text": "🎮 Начать игру",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def lucky_strike_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "⚽ Сделать удар",
                 "callback_data": "do_strike"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def do_strike_kb(tasks: list) -> aiogram.types.InlineKeyboardMarkup:


        schema = []
        btns = []

        if "b3" in tasks:
            schema.append(1)
            btns.append({"text": "💵 Купить 3 удара",
                 "callback_data": "4"})
        if "no_b3" in tasks:
            schema.append(1)
            btns.append({"text": "⚽ Сделать удар",
                         "callback_data": "do_strike"})
        if "back" in tasks:
            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "games"})
        if "take_card" in tasks:
            schema.append(1)
            btns.append({"text": "🃏 Получить карту",
                         "callback_data": "get_new_cards"})

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def rate_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1,1]
        btns = [{"text": "🃏 Рейтинг коллекционеров карточек",
                 "callback_data": "rate_card"},
                {"text": "⚽ Рейтинг игроков в Пенальти",
                 "callback_data": "rate_pen"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def trade_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "🃏 Выбрать карту для обмена",
                 "callback_data": "chan_by_0"},
                {"text": "❌ Отклонить обмен",
                 "callback_data": "trade_canc"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_second_user_for_offer_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "🧑💻 В личный кабинет",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def pen_canc_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "🧑💻 В личный кабинет",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def time_events_checker_2_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "🃏 Получить карту",
                 "callback_data": "0"},
                {"text": "🧑💻 В личный кабинет",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def time_events_checker_kb(res=True) -> aiogram.types.InlineKeyboardMarkup:

        if res:
            schema = [1,1]
            btns = [{"text": "🧑💻 В личный кабинет",
                     "callback_data": "back"},
                    {"text": "⚽ Рейтинг игроков в Пенальти",
                     "callback_data": "rate_pen"}
                    ]
        else:
            schema = [1]
            btns = [{"text": "🧑💻 В личный кабинет",
                     "callback_data": "back"}
                    ]


        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def pen_start_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [3]
        btns = [{"text": "1⃣",
                 "callback_data": "pen_1"},
                {"text": "2⃣",
                 "callback_data": "pen_2"},
                {"text": "3⃣",
                 "callback_data": "pen_3"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def pen_else_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [3]
        btns = [{"text": "1⃣",
                 "callback_data": "pen_1"},
                {"text": "2⃣",
                 "callback_data": "pen_2"},
                {"text": "3⃣",
                 "callback_data": "pen_3"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def pen_finished_0_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "⚽ Переигровка",
                 "callback_data": "penalti"},
                {"text": "🏳 Ничья",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def pen_finished_1_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "🧑💻 В личный кабинет",
                 "callback_data": "back"},
                {"text": "⚽ Рейтинг игроков в Пенальти",
                 "callback_data": "rate_pen"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def insert_card_to_offer_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "✅ Принять",
                 "callback_data": "trade"},
                {"text": "❌ Отклонить обмен",
                 "callback_data": "trade_canc"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_show_new_cards_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "✅ Принять",
                 "callback_data": "trade"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_to_getcar_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "⏪ Назад",
                 "callback_data": "getcar"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def show_card_one_by_one_kb(tasks: list, add_data: dict) -> aiogram.types.InlineKeyboardMarkup:

        schema = []
        btns = []

        if "sort_button" in tasks:
            schema.append(1)
            btns.append(add_data['sort_button'])

        if "Выбрать для обмена" in tasks:
            schema.append(1)
            btns.append(
                {"text": "Выбрать для обмена",
                 "callback_data": add_data['Выбрать для обмена']})


        if "not_chan" in tasks:
            schema.append(5)
            btns.append({"text": "<<",
                         "callback_data": add_data['<<<']})
            btns.append({"text": "<",
                         "callback_data": add_data['<<']})
            btns.append(
                {"text": ">",
                 "callback_data": add_data['>>']}
            )
            btns.append(
                {"text": ">>",
                 "callback_data": add_data['>>>']}
            )

        if "num1" in tasks:

            schema.append(1)
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )

        if "num1_chan" in tasks:
            schema.append(1)
            btns.append({"text": "❌ Отклонить обмен",
                         "callback_data": "trade_canc"})

        if "num1_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})


        if "num0" in tasks:

            schema.append(3)
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )
            btns.append(
                {"text": ">",
                 "callback_data": add_data['>>']}
            )
            btns.append(
                {"text": ">>",
                 "callback_data": add_data['>>>']}
            )

        if "num0_chan" in tasks:
            schema.append(1)
            btns.append({"text": "❌ Отклонить обмен",
                         "callback_data": "trade_canc"})

        if "num0_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        if "num_len-1" in tasks:
            schema.append(3)
            btns.append({"text": "<<",
                         "callback_data": add_data['<<<']})
            btns.append({"text": "<",
                         "callback_data": add_data['<<']})
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )

        if "num_len-1_chan" in tasks:
            schema.append(1)
            btns.append({"text": "❌ Отклонить обмен",
                         "callback_data": "trade_canc"})

        if "num_len-1_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        if "num_else" in tasks:
            schema.append(5)
            btns.append({"text": "<<",
                         "callback_data": add_data['<<<']})
            btns.append({"text": "<",
                         "callback_data": add_data['<<']})
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )
            btns.append(
                {"text": ">",
                 "callback_data": add_data['>>']}
            )
            btns.append(
                {"text": ">>",
                 "callback_data": add_data['>>>']}
            )

        if "num_else_chan" in tasks:
            schema.append(1)
            btns.append({"text": "❌ Отклонить обмен",
                         "callback_data": "trade_canc"})

        if "num_else_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})


        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def show_card_by_rare_kb(tasks: list, add_data: dict) -> aiogram.types.InlineKeyboardMarkup:

        schema = []
        btns = []


        if "num1" in tasks:
            schema.append(1)
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )

        if "num1_chan" in tasks:
            schema.append(1)
            btns.append({"text": "❌ Отклонить обмен",
                         "callback_data": "trade_canc"})

        if "num1_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        if "num0" in tasks:
            schema.append(3)
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )
            btns.append(
                {"text": ">",
                 "callback_data": add_data['>>']}
            )
            btns.append(
                {"text": ">>",
                 "callback_data": add_data['>>>']}
            )

        if "num0_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        if "num_len-1" in tasks:
            schema.append(3)
            btns.append({"text": "<<",
                         "callback_data": add_data['<<<']})
            btns.append({"text": "<",
                         "callback_data": add_data['<<']})
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )


        if "num_len-1_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        if "num_else" in tasks:
            schema.append(5)
            btns.append({"text": "<<",
                         "callback_data": add_data['<<<']})
            btns.append({"text": "<",
                         "callback_data": add_data['<<']})
            btns.append(
                {"text": add_data["num1_text"],
                 "callback_data": add_data["num1_data"]}
            )
            btns.append(
                {"text": ">",
                 "callback_data": add_data['>>']}
            )
            btns.append(
                {"text": ">>",
                 "callback_data": add_data['>>>']}
            )

        if "num_else_not_chan" in tasks:

            schema.append(1)
            btns.append({"text": "⏪ Назад",
                         "callback_data": "my_collection"})

        return InlineButtons._create_kb(btns, schema)
    @staticmethod
    def take_card_kb(have_cards=False) -> aiogram.types.InlineKeyboardMarkup:
        schema = []
        btns = []

        if have_cards:
            schema.append(1)
            schema.append(1)
            schema.append(1)
            btns.append({"text": "🃏 Получить карту",
                     "callback_data": "getcar"})
            btns.append({"text": "\U0001F4F2 Начать просмотр по карточкам",
                     "callback_data": "one_by_0"})
            btns.append({"text": "⏪ Назад",
                     "callback_data": "back"})

        else:
            schema = [1, 1]
            btns = [{"text": "🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "⏪ Назад",
                     "callback_data": "back"}
                    ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def games_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1, 1]
        btns = [{"text": "⚽ Пенальти",
                 "callback_data": "penalti"},
                {"text": "☘ Удачный удар",
                 "callback_data": "lucky_strike"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def info_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1,1,1]
        btns = [{"text": "🃏 О картах",
                 "callback_data": "card_info"},
                {"text": "⚽ О пенальти",
                 "callback_data": "penalti_info"},
                {"text": "☘ Об удачном ударе",
                 "callback_data": "strike_info"},
                {"text": "⏪ Назад",
                 "callback_data": "menu"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def call_trade_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1, ]
        btns = [{"text": "🎭 Обмен картами",
                 "callback_data": "chan_by_0"},
                {"text": "🧑💻 В личный кабинет",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_buy_message_kb(redirect_uri) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1,1]
        btns = [{"text": "Оплатить",
                 "url": redirect_uri},
                {"text": "Проверить оплату",
                 "callback_data": "check_pay"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def card_shop_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [
                {"text": "🛍 Магазин карточек",
                 "callback_data": "store"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def user_game_kb(user_in_game: bool) -> aiogram.types.InlineKeyboardMarkup:
        if not user_in_game:
            schema = [1, 1]
            btns = [
                {"text": "✅ Начать игру",
                 "callback_data": "pen_start"},
                {"text": "❌ Отклонить",
                 "callback_data": "pen_canc"}
            ]
        else:
            schema = [1, 1]
            btns = [
                {"text": "ПЕНАЛЬТИ⚽",
                 "callback_data": "penalti"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
            ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_back_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [
            {"text": "⏪ Назад",
             "callback_data": "back"}
        ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def mini_games_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [
            {"text": "🎲 Мини-игры",
             "callback_data": "games"}
        ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_cards_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [
            {"text": "\U0001F0CF Получить карточки \U0001F0CF",
             "callback_data": "get_new_cards"}
        ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def show_new_card_kb(card_info=True) -> aiogram.types.InlineKeyboardMarkup:
        if card_info:
            schema = [1]
            btns = [
                {"text": "✅ Принять",
                 "callback_data": "back"}
            ]
        else:
            schema = [1]
            btns = [
                {"text": "Дальше \U0001F449",
                 "callback_data": "slide_bought_cards"}
            ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def getcar_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1, 1, 1]
        btns = [{"text": "🎁 Получить бесплатную карточку",
                 "callback_data": "0"},
                {"text": "🛍 Магазин карточек",
                 "callback_data": "store"},
                {"text": "🧑‍💻 Ввести промокод",
                 "callback_data": "input"},
                {"text": "⏪ Назад",
                 "callback_data": "back"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def store_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1, 1, 1]
        btns = [{"text": "💵 Купить одну рандомную карточку",
                 "callback_data": "1"},
                {"text": "💵 Купить три рандомных карточки",
                 "callback_data": "2"},
                {"text": "💵 Купить пять рандомных карточек",
                 "callback_data": "3"},
                {"text": "⏪ Назад",
                 "callback_data": "back"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def rare_mode_kb(buttons: list) -> aiogram.types.InlineKeyboardMarkup:

        schema = []
        btns = []

        for button in buttons:
            schema.append(1)
            btns.append(button)

        schema.append(1)
        btns.append({"text": "⏪ Назад",
                 "callback_data": "back"})

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def collection_kb() -> aiogram.types.InlineKeyboardMarkup:

        schema = [1,1,1,1]
        btns = [{"text": "Все карты",
                 "callback_data": "one_by_0"},
                {"text": "По редкости",
                 "callback_data": "rare_mode"},
                {"text": "Посмотреть списком",
                 "callback_data": "coll"},
                {"text": "⏪ Назад",
                 "callback_data": "back"},
                ]

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_lk_kb(admin_status=False) -> aiogram.types.InlineKeyboardMarkup:

        if admin_status:
            schema = [2,2,1, 1, 1]
            btns = [{"text": "🧳 Моя коллекция",
                     "callback_data": "my_collection"},
                    {"text": "🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "🎭 Обмен картами",
                     "callback_data": "chan_by_0"},
                    {"text": "🏆 Общий рейтинг",
                     "callback_data": "rate"},
                    {"text": "🎲 Мини-игры",
                     "callback_data": "games"},
                    {"text": "Админская панель",
                     "callback_data": "admin"},
                    {"text": "⏪ Назад",
                     "callback_data": "menu"},
                    ]
        else:
            schema = [2,2, 1, 1]
            btns = [{"text": "🧳 Моя коллекция",
                     "callback_data": "my_collection"},
                    {"text": "🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "🎭 Обмен картами",
                     "callback_data": "chan_by_0"},
                    {"text": "🏆 Общий рейтинг",
                     "callback_data": "rate"},
                    {"text": "🎲 Мини-игры",
                     "callback_data": "games"},
                    {"text": "⏪ Назад",
                     "callback_data": "menu"},
                    ]
        return InlineButtons._create_kb(btns, schema)
