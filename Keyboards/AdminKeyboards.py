from typing import List

import aiogram.types

from Keyboards.InlineConsts import InlineConstructor
from Keyboards.ReplyConsts import DefaultConstructor


class InlineButtons(InlineConstructor):

    @staticmethod
    def get_admin_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1,1,1]
        btns = [{"text": "Карточки",
                 "callback_data":"admin_card"},
                {"text": "Промокоды",
                 "callback_data": "admin_promo"},
                {"text": "Пользователи",
                 "callback_data": "admin_users"},
                {"text": "⏪ Назад",
                 "callback_data": "back"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def users_processing_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "⏪ Назад",
                 "callback_data": "admin_users"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_username_for_admin_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "История покупок",
                 "callback_data": "get_user_hist_"},
                {"text": "⏪ Назад",
                 "callback_data": "admin_users"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_photo_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "Вернуться к панели",
                 "callback_data": "admin"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_new_photo_kb(card_status: bool) -> aiogram.types.InlineKeyboardMarkup:

        if not card_status:
            schema = [1]
            btns = [{"text": "Пропустить редактирование фото",
                     "callback_data": "admin"}

                    ]
        else:
            schema = [1]
            btns = [{"text": "Вернуться к панели",
                     "callback_data": "admin"}
                    ]

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def save_new_card_photo_kb(card_status: bool) -> aiogram.types.InlineKeyboardMarkup:

        if card_status:
            schema = [1]
            btns = [{"text": "Сохранить",
                     "callback_data": "admin"}

                    ]
        else:
            schema = [1]
            btns = [{"text": "В админскую панель",
                     "callback_data": "admin"}
                    ]

        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def set_card_photo_kb(card_id) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "Сохранить",
                 "callback_data": "back"},
                {"text": "Редактировать",
                 "callback_data": str(card_id) + "_new"},
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def adm_add_card_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1]
        btns = [{"text": "⏪ Назад",
                 "callback_data": "admin"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def add_card_to_promo_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "️🧑💻 В личный кабинет",
                 "callback_data": "back"},
                {"text": "К получению карточек",
                 "callback_data": "getcar"}
                ]
        return InlineButtons._create_kb(btns, schema)



    @staticmethod
    def check_promo_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "️🧑💻 В личный кабинет",
                 "callback_data": "back"},
                {"text": "⏪ Назад",
                 "callback_data": "getcar"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def get_promo_text_kb(promo_id) -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "️Выбрать карточку",
                 "callback_data": "choose_" + str(promo_id) + "_0"},
                {"text": "Рандомная карточка",
                 "callback_data": "promo_" + str(promo_id) + "_rng"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def adm_update_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1,1]
        btns = [{"text": "Выбрать карточку",
                 "callback_data": "redact_62_0"},
                {"text": "⏪ Назад",
                 "callback_data": "admin"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def adm_del_card_kb() -> aiogram.types.InlineKeyboardMarkup:
        schema = [1, 1]
        btns = [{"text": "Выбрать карточку",
                 "callback_data": "destroy_62_0"},
                {"text": "⏪ Назад",
                 "callback_data": "admin"}
                ]
        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def adm_del_promo_kb(promos_for_kb: List[dict] | None) -> aiogram.types.InlineKeyboardMarkup:
        schema = []
        btns = []

        if promos_for_kb:
            for promo in promos_for_kb:
                schema.append(1)
                btns.append(promo)

        schema.append(1)
        btns.append({"text": "⏪ Назад",
                 "callback_data": "admin"})

        return InlineButtons._create_kb(btns, schema)


    @staticmethod
    def admin_sections_kb(tasks: list, add_data: dict) -> aiogram.types.InlineKeyboardMarkup:

        schema = []
        btns = []

        if "not_section" in tasks:
            section = add_data['section']
            schema.append(1)
            btns.append({"text": "Добавить",
                     "callback_data":"adm_add_" + section})
            # btns.append({"text": "Удалить",
            #          "callback_data": "adm_del_" + section})

        if "card" in tasks:
            schema.append(1)
            schema.append(1)
            btns.append({"text": "Редактировать",
                     "callback_data": "adm_update"})
            btns.append({"text": "⏪ Назад",
                     "callback_data": "admin"})


        if "not_card" in tasks:
            schema.append(1)
            btns.append({"text": "⏪ Назад",
                     "callback_data": "admin"})

        if "section" in tasks:
            schema.append(1)
            schema.append(1)
            btns.append({"text": "Инфо по юзеру",
                     "callback_data":"get_user"})
            btns.append({"text": "⏪ Назад",
                     "callback_data": "admin"})


        return InlineButtons._create_kb(btns, schema)

    @staticmethod
    def show_all_cards_kb(tasks: list, buttons: dict) -> aiogram.types.InlineKeyboardMarkup:

        schema = []
        btns = []

        if "sort_button" in tasks:
            schema.append(1)
            btns.append(buttons['sort_button'])

        if "num_0" in tasks:

            if "destroy_" in tasks:
                schema.append(1)
                btns.append(buttons['del_btn'])

            else:
                schema.append(1)
                btns.append(buttons['choose_btn'])

            schema.append(2)
            btns.append(buttons['num_btn'])
            btns.append(buttons['next_btn'])

        if "num_len-1" in tasks:
            if "destroy_" in tasks:
                schema.append(1)
                btns.append(buttons['del_btn'])

            else:
                schema.append(1)
                btns.append(buttons['choose_btn'])

            schema.append(2)
            btns.append(buttons['back_btn'])
            btns.append(buttons['num_btn'])

        if "num_else" in tasks:
            if "destroy_" in tasks:
                schema.append(1)
                btns.append(buttons['del_btn'])

            else:
                schema.append(1)
                btns.append(buttons['choose_btn'])

            schema.append(3)
            btns.append(buttons['back_btn'])
            btns.append(buttons['num_btn'])
            btns.append(buttons['next_btn'])

        schema.append(1)
        btns.append({"text": "⏪ Назад",
                     "callback_data": "admin"})

        return InlineButtons._create_kb(btns, schema)


