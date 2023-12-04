import random

from sqlalchemy import select, update, delete

from Databases.DB import *


async def place_promo(promo_text: str, usages: str):
    async with async_session() as session:

        async with session.begin():
            # Create a new Promo instance
            new_promo = Promo(promo_id=random.randint(10000000,10000000000), promo=promo_text, usages=usages)
            session.add(new_promo)
            await session.commit()

        # Query the newly created Promo to get its ID
        result = await session.execute(select(Promo).where(Promo.promo == promo_text))
        promo = result.scalars().first()
        return promo.promo_id if promo else None

async def select_all_cards(sort_mode: str | None):
    async with async_session() as session:

        if sort_mode == "Down":
            result = await session.execute(select(Card))

            cards = result.scalars().all()
            cards = sorted(cards, key=lambda card: card.points, reverse=True)
            return cards

        elif sort_mode == "Up":
            result = await session.execute(select(Card))
            cards = result.scalars().all()
            cards = sorted(cards, key=lambda card: card.points, reverse=False)
            return cards

        else:
            result = await session.execute(select(Card))
            cards = result.scalars().all()

            return cards


async def insert_promo_card(promo_id: int, card_id: int):
    async with async_session() as session:
        async with session.begin():

            if card_id == 0:

                card_result = await session.execute(select(Card))
                cards = card_result.scalars().all()

                await session.execute(
                    update(Promo).where(Promo.promo_id == promo_id).values(card_id=random.choice(cards).card_id)
                )
                await session.commit()

            else:

                await session.execute(
                    update(Promo).where(Promo.promo_id == promo_id).values(card_id=card_id)
                )
                await session.commit()

async def check_promo_(tele_id: int, input_str: str):
    async with async_session() as session:
        async with session.begin():
            # Query the promo
            result = await session.execute(select(Promo).where(Promo.promo == input_str))
            res = result.scalar_one_or_none()

            # Check the promo validity
            if res is None or (res.usages != "INF" and int(res.usages) <= 0):
                return [False, -1]
            else:
                promo_check_result = await session.execute(
                    select(CheckPromo).where(
                        CheckPromo.promo == input_str,
                        CheckPromo.tele_id == tele_id
                    )
                )
                promo_check = promo_check_result.scalar_one_or_none()

                if promo_check is not None:
                    return [False, -1]

                # Insert into check_promo if the promo is valid and not used by this tele_id
                new_check_promo = CheckPromo(id = random.randint(10000000,10000000000),tele_id=tele_id, promo=input_str)
                session.add(new_check_promo)
                await session.commit()

                return [True, res.card_id]

async def minus_promo_usages(input_str: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Promo).where(Promo.promo == input_str))
            res = result.scalar_one_or_none()
            if res and res.usages != "INF":
                new_usages = int(res.usages) - 1
                if new_usages <= 0:
                    await session.delete(res)
                else:
                    res.usages = str(new_usages)
                await session.commit()

async def select_all_promos():
    async with async_session() as session:
        result = await session.execute(select(Promo))
        promos = result.scalars().all()
        card_list = []
        for promo in promos:
            if promo.card_id != 0:
                card_result = await session.execute(select(Card).where(Card.card_id == promo.card_id))
                card = card_result.scalar_one()
                card_list.append(card)
            else:
                card_list.append(None)  # or a placeholder for a random card
        return [promos, card_list]

async def delete_promo(promo_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Promo).where(Promo.promo_id == promo_id))
            res = result.scalar_one_or_none()
            if res:
                await session.delete(res)
                await session.execute(delete(CheckPromo).where(CheckPromo.promo == res.promo))
                await session.commit()

async def add_card_to_user_by_card_id(card_id: int, tele_id: int):
    async with async_session() as session:
        async with session.begin():
            new_card_of_user = CardsOfUser(tele_id=tele_id, card_id=card_id, is_new=True)
            session.add(new_card_of_user)
            await session.commit()

async def get_user_info(tele_id: int, user_name: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tele_id == tele_id))
        user = result.scalar_one_or_none()
        if user:
            user_str = f"Данные по пользователю - {user_name}:\n\n" \
                       f"Телеграмм id - {tele_id}\n" \
                       f"Дата регистрации - {user.register_at}\n" \
                       f"Собранное количество карточек - {user.card_num}\n" \
                       f"Рейтинг собранных карточек - {user.card_rating}\n" \
                       f"Рейтинг в игре пенальти - {user.penalty_rating}\n\n" \
                       f"Забирал бесплатную карточку - {user.free_card}\n" \
                       f"Количество транзакций - {user.transactions}"
            return user_str
        return "Пользователь не найден"


async def get_user_transactions_info(tele_id: int, user_name: str):
    async with async_session() as session:
        result = await session.execute(select(Operation).where(Operation.user_id == tele_id, Operation.finished == True))
        transactions = result.scalars().all()
        trans_info = f"Информация о покупках пользователя - @{user_name}:\n\n"
        if not transactions:
            return f"Пока что пользователь - @{user_name} не совершал покупок"
        for idx, trans in enumerate(transactions, start=1):
            pack_result = await session.execute(select(Pack).where(Pack.buy_id == int(trans.operation_id)))
            pack = pack_result.scalar_one()
            trans_info += f"{idx}. {pack.name}\n"
        return trans_info

async def delete_card_(card_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Card).where(Card.card_id == card_id))
            await session.execute(delete(CardsOfUser).where(CardsOfUser.card_id == card_id))
            await session.commit()


