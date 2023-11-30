from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):

    check_promo = State()
    get_promo_text = State()
    get_second_user_for_offer = State()
    get_username_for_pen = State()
    get_username_for_admin = State()
    get_photo = State()
    save_card_photo = State()
    get_new_photo = State()
    save_new_card_photo = State()
    get_show_new_cards = State()



