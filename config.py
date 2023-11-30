import random

from sqlalchemy import select, update, delete, and_
import datetime

from Databases.DB import *

class Card_:
    def __init__(self, card_id):
        self.id = card_id
        self.num = 1

    def plus(self, card_id):
        if card_id == self.id:
            self.num += 1

    def __str__(self):
        return '[' + str(self.id) + ', ' + str(self.num) + " шт]"




def get_rareness_by_num(num):
    if num == 0:
        return "ОБЫЧНАЯ"
    if num == 1:
        return "НЕОБЫЧНАЯ"
    if num == 2:
        return "ЭПИЧЕСКАЯ"
    if num == 3:
        return "УНИКАЛЬНАЯ"
    if num == 4:
        return "ЛЕГЕНДАРНАЯ"
    if num == 5:
        return "РЕДКАЯ"

    return None


def get_rareness_by_str(rare_string):
    rare_str = rare_string.lower().replace(" ", "")
    if rare_str == "обычная":
        return 0
    if rare_str == "необычная":
        return 1
    if rare_str == "эпическая":
        return 2
    if rare_str == "уникальная":
        return 3
    if rare_str == "легендарная":
        return 4
    if rare_str == "редкая":
        return 5

    return None


def check_card_info(player_info):
    if get_rareness_by_str(player_info[3]) is None:
        return -1
    if player_info[4].isdigit() is not True:
        return -1

    return 0

def get_rareness_by_random(rnd_num):
    if rnd_num < 30:
        return 0
    if rnd_num < 55:
        return 1
    if rnd_num < 75:
        return 5
    if rnd_num < 90:
        return 2
    if rnd_num < 99:
        return 3
    if rnd_num < 100:
        return 4




async def calc_card_rating(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            cards_result = await session.execute(select(CardsOfUser).where(CardsOfUser.tele_id == tele_id))
            cards_of_user = cards_result.scalars().all()
            rating = 0
            num = 0
            for card_user in cards_of_user:
                card_result = await session.execute(select(Card).where(Card.card_id == card_user.card_id))
                card = card_result.scalar_one()
                rating += card.points
                num += 1
            await session.execute(update(User).where(User.tele_id == tele_id).values(card_rating=rating, card_num=num))
            await session.commit()


async def place_user_in_bd(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            users_result = await session.execute(select(User).where(User.tele_id == tele_id))
            users_result = users_result.scalar_one_or_none()

            # print(users_result)

            if not users_result:
                register_at = datetime.date.today()
                new_user = User(tele_id=tele_id, card_num=0, card_rating=0, penalty_rating=100, register_at=register_at)
                session.add(new_user)
                await session.commit()


async def clear_non_active_users():
    async with async_session() as session:
        async with session.begin():
            current_date = datetime.date.today()
            users_result = await session.execute(select(User).where(and_(User.card_num == 0, User.penalty_rating == 0)).order_by(User.register_at))
            users = users_result.scalars().all()
            for user in users:
                reg_date = user.register_at
                if (current_date - reg_date).days >= 30:
                    await session.delete(user)
            await session.commit()

async def search_user_in_db(tele_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tele_id == tele_id))
        return result.scalar_one_or_none()

async def select_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def get_top_places_():
    async with async_session() as session:
        card_top_result = await session.execute(select(User).order_by(User.card_rating.desc()).limit(10))
        card_top = card_top_result.scalars().all()

        penalti_top_result = await session.execute(select(User).order_by(User.penalty_rating.desc()).limit(10))
        penalti_top = penalti_top_result.scalars().all()

        return [card_top, penalti_top]

async def get_user_places(tele_id: int):
    async with async_session() as session:
        card_rating_result = await session.execute(select(User).order_by(User.card_rating.desc()))
        card_rating_users = card_rating_result.scalars().all()
        card_rank = next((i + 1 for i, user in enumerate(card_rating_users) if user.tele_id == tele_id), None)

        penalty_rating_result = await session.execute(select(User).order_by(User.penalty_rating.desc()))
        penalty_rating_users = penalty_rating_result.scalars().all()
        penalty_rank = next((i + 1 for i, user in enumerate(penalty_rating_users) if user.tele_id == tele_id), None)

        return [card_rank, penalty_rank]


async def insert_lk_message_id(lk_message_id: int, tele_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(User).where(User.tele_id == tele_id).values(lk_message_id=lk_message_id))
            await session.commit()

async def search_user_cards(tele_id: int):
    async with async_session() as session:
        cards_of_user_result = await session.execute(select(CardsOfUser).where(CardsOfUser.tele_id == tele_id))
        cards_of_user = cards_of_user_result.scalars().all()
        card_list = []
        for card_user in cards_of_user:
            card_result = await session.execute(select(Card).where(Card.card_id == card_user.card_id))
            card = card_result.scalar_one_or_none()
            if card:
                card_list.append(card)
        return card_list

async def get_user_card_list(tele_id: int):
    async with async_session() as session:
        cards_of_user_result = await session.execute(select(CardsOfUser).where(CardsOfUser.tele_id == tele_id))
        cards_of_user = cards_of_user_result.scalars().all()
        if not cards_of_user:
            return None

        ans = []
        for card_user in cards_of_user:

            num = 0
            for res in ans:
                if res.id == card_user.card_id:
                    num += 1
                    res.plus(card_user.card_id)
            if num == 0:
                ans.append(Card_(card_user.card_id))

        card_list = []
        for card in ans:
            card_result = await session.execute(select(Card).where(Card.card_id == card.id))
            card_list.append(card_result.scalar_one())

        return [card_list, ans]

async def get_lk_id_message(tele_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tele_id == tele_id))
        user = result.scalar_one_or_none()
        return user.lk_message_id if user else None


async def get_operation_id(tele_id: int, product_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tele_id == tele_id))
        user = result.scalar_one_or_none()
        if user:
            id_str = f"{user.tele_id}|{product_id}|{user.transactions}"
            return id_str
        return None


async def get_price(prod_id: int):
    async with async_session() as session:
        result = await session.execute(select(Pack.cost).where(Pack.buy_id == prod_id))
        pack = result.scalar_one_or_none()
        return pack.cost if pack else None

async def is_admin(tele_id: int):
    async with async_session() as session:
        result = await session.execute(select(Admin).where(Admin.tele_id == tele_id))
        return result.scalar_one_or_none() is not None

async def place_player_in_db(player_info):
    async with async_session() as session:
        async with session.begin():
            new_card = Card(
                card_id = random.randint(1000000000,1000000000000),
                player_name=player_info[0],
                player_nickname=player_info[1],
                team=player_info[2],
                rareness=int(get_rareness_by_str(player_info[3])),
                points=int(player_info[4]),
                created_at=datetime.date.today()
            )
            session.add(new_card)
            await session.commit()
        return new_card


async def set_card_photo(card_id: int, photo_id: str):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Card).where(Card.card_id == card_id).values(photo_id=photo_id))
            await session.commit()
        return 0

async def get_card_by_id(card_id: int):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.card_id == card_id))
        new_card = result.scalar_one_or_none()
        if new_card:
            card_info_str = f"Имя: {new_card.player_name}\nНикнейм: {new_card.player_nickname}\nКоманда: {new_card.team}" \
                            f"\nРедкость: {get_rareness_by_num(new_card.rareness)}\nРейтинг: {new_card.points}"
            return [card_info_str, new_card.photo_id]
        return None

async def edit_card_in_db(card_id: int, new_info):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(Card)
                .where(Card.card_id == card_id)
                .values(
                    player_name=new_info[0],
                    player_nickname=new_info[1],
                    team=new_info[2],
                    rareness=get_rareness_by_str(new_info[3]),
                    points=new_info[4],
                    updated_at=datetime.date.today()
                )
            )
            await session.commit()
        return 0





async def add_cards_to_user(card_list, user_id: int):
    async with async_session() as session:
        async with session.begin():
            for card in card_list:
                new_card_of_user = CardsOfUser(card_key= random.randint(1000000000,1000000000000),
                                               tele_id=user_id,
                                               card_id=card.card_id,
                                               is_new=True)
                session.add(new_card_of_user)
            await session.commit()

async def user_in_top_ten(tele_id: int):
    async with async_session() as session:
        ans = [False, False]

        card_top_result = await session.execute(select(User).order_by(User.card_rating.desc()).limit(10))
        card_top = card_top_result.scalars().all()
        for user in card_top:
            if user.tele_id == tele_id:
                ans[0] = True

        penalty_top_result = await session.execute(select(User).order_by(User.penalty_rating.desc()).limit(10))
        penalty_top = penalty_top_result.scalars().all()
        for user in penalty_top:
            if user.tele_id == tele_id:
                ans[1] = True

        return ans

async def place_operation_in_db(tele_id: int, order_id: str, order_name: str):
    async with async_session() as session:
        async with session.begin():
            new_operation = Operation(operation_id=order_id, operation_name=order_name, user_id=tele_id)
            session.add(new_operation)
            await session.commit()

async def get_active_transaction(tele_id: int):
    async with async_session() as session:
        result = await session.execute(select(Operation).where(and_(Operation.user_id == tele_id, Operation.finished == False)))
        operation = result.scalar_one_or_none()
        return operation.operation_id if operation else None

async def save_transaction(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Operation).where(Operation.user_id == tele_id).values(finished=True))
            await session.commit()

async def get_last_cards(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            cards_of_user_result = await session.execute(select(CardsOfUser).where(and_(CardsOfUser.tele_id == tele_id, CardsOfUser.is_new == True)))
            cards_of_user = cards_of_user_result.scalars().all()

            if not cards_of_user:
                return [None, 0]

            for card_user in cards_of_user:
                card_user.is_new = False

            card_result = await session.execute(select(Card).where(Card.card_id == cards_of_user[0].card_id))
            card = card_result.scalar_one()
            await session.commit()

        return [card, len(cards_of_user)]

async def clear_user_transaction(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            try:

                await session.execute(delete(Operation).where(and_(Operation.user_id == tele_id, Operation.finished == False)))
                await session.commit()
                print(f"Очищены транзакции пользователя {tele_id}")
            except:
                print(f"Не получилось почистить транзакции пользователя {tele_id} (возможно их нет)")


async def plus_user_transactions(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(User).where(User.tele_id == tele_id).values(transactions=User.transactions + 1))
            await session.commit()

async def check_free_card(tele_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tele_id == tele_id))
        user = result.scalar_one_or_none()
        if user and user.free_card:
            datefstr = user.free_card
            delta = datetime.datetime.now() - datefstr
            if delta.days >= 1:
                return [True, None]
            return [False, str(datetime.timedelta(hours=24) - delta)]
        return [True, None]


async def push_free_card_date(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(User).where(User.tele_id == tele_id).values(free_card=datetime.datetime.now()))
            await session.commit()


async def create_new_change_offer(user1_id: int, card_id: int):
    async with async_session() as session:
        async with session.begin():
            new_offer = Offer(tele_id1=user1_id, agree1=False, agree2=False, card_id=card_id)
            session.add(new_offer)
            await session.commit()


async def get_user_change_num(tele_id: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where(Offer.tele_id1 == tele_id))
        if offer_result.scalar_one_or_none() is not None:
            return 1
        offer_result = await session.execute(select(Offer).where(Offer.tele_id2 == tele_id))
        if offer_result.scalar_one_or_none() is not None:
            return 2
        return None

async def insert_second_user(tele_id1: int, tele_id2: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Offer).where(Offer.tele_id1 == tele_id1).values(tele_id2=tele_id2))
            await session.commit()

async def is_offer_defined(tele_id: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where((Offer.tele_id1 == tele_id) | (Offer.tele_id2 == tele_id)))
        return offer_result.scalar_one_or_none() is not None

async def user_had_offer(tele_id: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where(Offer.tele_id2 == tele_id))
        return offer_result.scalar_one_or_none() is not None

async def second_user_had_card(tele_id2: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where(Offer.tele_id2 == tele_id2))
        offer = offer_result.scalar_one_or_none()
        if offer is None:
            return -1
        return offer.card_id2 is not None

async def add_card_to_offer(tele_id: int, card_id: int):
    async with async_session() as session:
        async with session.begin():
            offer_result = await session.execute(select(Offer).where(Offer.tele_id1 == tele_id))
            if offer_result.scalar_one_or_none() is not None:
                await session.execute(update(Offer).where(Offer.tele_id1 == tele_id).values(card_id1=card_id))
            else:
                await session.execute(update(Offer).where(Offer.tele_id2 == tele_id).values(card_id2=card_id))
            await session.commit()

async def get_trade_card(tele_id: int, num: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where(Offer.tele_id1 == tele_id))
        offer = offer_result.scalar_one_or_none()
        if offer:
            card_id = offer.card_id1 if num == 0 else offer.card_id2
            card_result = await session.execute(select(Card).where(Card.card_id == card_id))
            return card_result.scalar_one_or_none()
        return None

async def get_first_user(tele_id2: int):
    async with async_session() as session:
        offer_result = await session.execute(select(Offer).where(Offer.tele_id2 == tele_id2))
        offer = offer_result.scalar_one_or_none()
        return offer.tele_id1 if offer else None

async def cancel_trade(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            offer_result = await session.execute(select(Offer).where(Offer.tele_id1 == tele_id))
            offer = offer_result.scalar_one_or_none()
            if offer is None:
                offer_result = await session.execute(select(Offer).where(Offer.tele_id2 == tele_id))
                offer = offer_result.scalar_one_or_none()
            if offer:
                await session.delete(offer)
                await session.commit()


        if offer:
            return [offer.tele_id1, offer.tele_id2]

        return [0, 0]

async def do_trade(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            offer_result = await session.execute(select(Offer).where(Offer.tele_id1 == tele_id))
            offer = offer_result.scalar_one_or_none()
            if offer:
                card_of_user_result = await session.execute(select(CardsOfUser).where(and_(CardsOfUser.tele_id == offer.tele_id1, CardsOfUser.card_id == offer.card_id1)))
                card_user1 = card_of_user_result.scalar_one()
                card_user1.tele_id = offer.tele_id2

                card_of_user_result = await session.execute(select(CardsOfUser).where(and_(CardsOfUser.tele_id == offer.tele_id2, CardsOfUser.card_id == offer.card_id2)))
                card_user2 = card_of_user_result.scalar_one()
                card_user2.tele_id = offer.tele_id1

                await session.delete(offer)
                await session.commit()

        if offer:
            return [offer.tele_id1, offer.tele_id2]

        return [0, 0]

async def get_users_id_for_free_card():
    async with async_session() as session:
        user_list = []
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            if (await check_free_card(user.tele_id))[0] and user.get_messages == 0:
                user_list.append(user.tele_id)
        return user_list


async def set_get_msg(tele_id: int, value: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(User).where(User.tele_id == tele_id).values(get_messages=value))
            await session.commit()


