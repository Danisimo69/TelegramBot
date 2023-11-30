

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
        btns = [{"text": "️ℹ️ Информация",
                 "callback_data": "info"},
                {"text": "️🎮 Начать игру",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def lucky_strike_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "️⚽️ Сделать удар",
                 "callback_data": "do_strike"},
                {"text": "️⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def do_strike_kb(tasks: list) -> aiogram.types.InlineKeyboardMarkup:


        schema = []
        btns = []

        if "b3" in tasks:
            schema.append(1)
            btns.append({"text": "️💵 Купить 3 удара",
                 "callback_data": "4"})
        if "no_b3" in tasks:
            schema.append(1)
            btns.append({"text": "️⚽️ Сделать удар",
                         "callback_data": "do_strike"})
        if "back" in tasks:
            schema.append(1)
            btns.append({"text": "️⏪ Назад",
                         "callback_data": "games"})
        if "take_card" in tasks:
            schema.append(1)
            btns.append({"text": "️🃏 Получить карту",
                         "callback_data": "get_new_cards"})

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def rate_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1,1]
        btns = [{"text": "️🃏 Рейтинг коллекционеров карточек",
                 "callback_data": "rate_card"},
                {"text": "️⚽️ Рейтинг игроков в Пенальти",
                 "callback_data": "rate_pen"},
                {"text": "️⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "️⏪ Назад",
                 "callback_data": "menu"}
                ]
        return InlineButtons._create_kb(btns, schema)



    @staticmethod
    def take_card_kb(have_cards=False) -> aiogram.types.InlineKeyboardMarkup:

        if have_cards:
            schema = [1,1,1]
            btns = [{"text": "️🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "\U0001F4F2 Начать просмотр по карточкам",
                     "callback_data": "one_by_0"},
                    {"text": "️⏪ Назад",
                     "callback_data": "back"}
                    ]
        else:
            schema = [1, 1]
            btns = [{"text": "️🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "️⏪ Назад",
                     "callback_data": "back"}
                    ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def games_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1, 1]
        btns = [{"text": "⚽️ Пенальти",
                 "callback_data": "penalti"},
                {"text": "️☘️ Удачный удар",
                 "callback_data": "lucky_strike"},
                {"text": "️⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def info_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1,1,1]
        btns = [{"text": "️🃏 О картах",
                 "callback_data": "card_info"},
                {"text": "️⚽️ О пенальти",
                 "callback_data": "penalti_info"},
                {"text": "️☘️ Об удачном ударе",
                 "callback_data": "strike_info"},
                {"text": "⏪ Назад",
                 "callback_data": "menu"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def back_lk_kb(admin_status=False) -> aiogram.types.InlineKeyboardMarkup:

        if admin_status:
            schema = [2,2,1, 1, 1]
            btns = [{"text": "️🧳 Моя коллекция",
                     "callback_data": "one_by_0"},
                    {"text": "️🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "️🎭 Обмен картами",
                     "callback_data": "chan_by_0"},
                    {"text": "️🏆 Общий рейтинг",
                     "callback_data": "rate"},
                    {"text": "️🎲 Мини-игры",
                     "callback_data": "games"},
                    {"text": "️Админская панель",
                     "callback_data": "admin"},
                    {"text": "⏪ Назад",
                     "callback_data": "menu"},
                    ]
        else:
            schema = [2,2, 1, 1]
            btns = [{"text": "️🧳 Моя коллекция",
                     "callback_data": "one_by_0"},
                    {"text": "️🃏 Получить карту",
                     "callback_data": "getcar"},
                    {"text": "️🎭 Обмен картами",
                     "callback_data": "chan_by_0"},
                    {"text": "️🏆 Общий рейтинг",
                     "callback_data": "rate"},
                    {"text": "️🎲 Мини-игры",
                     "callback_data": "games"},
                    {"text": "⏪ Назад",
                     "callback_data": "menu"},
                    ]
        return InlineButtons._create_kb(btns, schema)

class BasicButtons(DefaultConstructor):
    @staticmethod
    def back() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["◀️Назад"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1]
        btns = ["◀️Назад", "🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(
        add_back: bool = False, add_cancel: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        schema.append(1)
        btns.append("✅Подтвердить")
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def skip(
        add_back: bool = False, add_cancel: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["▶️Пропустить"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes(
        add_back: bool = False, add_cancel: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["✅Да"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def no(
        add_back: bool = False, add_cancel: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(
        add_back: bool = False, add_cancel: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2]
        btns = ["✅Да", "❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)