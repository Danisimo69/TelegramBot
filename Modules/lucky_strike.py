import traceback

from sqlalchemy import select, update
import datetime

import random

from Databases.DB import *
from Modules.config import get_rareness_by_str, generate_item_rarity


def get_rareness_by_random(rnd_num):
    if rnd_num < 30:
        return 0
    if rnd_num < 55:
        return 1
    if rnd_num < 80:
        return 5
    if rnd_num < 100:
        return 2


from sqlalchemy import and_


async def check_free_strike(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            lucky_strike_result = await session.execute(select(LuckyStrike).where(LuckyStrike.tele_id == tele_id))
            lucky_strike = lucky_strike_result.scalar_one_or_none()

            now = datetime.datetime.now()
            need_delta = datetime.timedelta(hours=4)

            if lucky_strike == None:
                new_strike = LuckyStrike(tele_id=tele_id, free_strike=now)
                session.add(new_strike)
                await session.commit()
                return [True, 0]

            free_strike_date = lucky_strike.free_strike
            if now - free_strike_date >= need_delta and lucky_strike.free_strikes > 0:
                lucky_strike.free_strike = now
                lucky_strike.free_strikes -= 1
                await session.commit()
                return [True, 0]

            remaining_time = need_delta - (
                        now - free_strike_date) if lucky_strike.free_strikes > 0 else datetime.timedelta(days=1) - (
                        now - free_strike_date)

            if '-' in str(remaining_time):
                lucky_strike.free_strike = now
                lucky_strike.free_strikes -= 1
                await session.commit()
                return [True, 0]
            else:
                return [False, str(remaining_time)]





async def check_purchased_strikes(tele_id: int):
    async with async_session() as session:
        lucky_strike_result = await session.execute(select(LuckyStrike).where(LuckyStrike.tele_id == tele_id))
        lucky_strike = lucky_strike_result.scalar_one_or_none()
        if lucky_strike and lucky_strike.purchased_strikes > 0:
            return [True, lucky_strike.purchased_strikes]
        return [False, 0]

async def give_free_strikes():

    while True:

        async with async_session() as session:
            async with session.begin():

                await session.execute(update(LuckyStrike).where(
                    datetime.datetime.now()-LuckyStrike.free_strike >= datetime.timedelta(hours=24)
                ).values(free_strikes=2))

                # users = await session.execute(select(LuckyStrike))
                # now = datetime.datetime.now()
                # for user in users.scalars().all():
                #     if (now - user.free_strike) >= datetime.timedelta(hours=12):
                #         user.free_strikes = 2

                await session.commit()

async def give_free_card():
    async with async_session() as session:
        async with session.begin():
            users = await session.execute(select(LuckyStrike))
            now = datetime.datetime.now()
            for user in users.scalars().all():
                if (now - user.free_strike).days >= 1:
                    user.free_strikes = 2
            await session.commit()

async def update_user_strikes(tele_id: int, num: int):
    async with async_session() as session:
        async with session.begin():
            if num == 1:
                await session.execute(update(LuckyStrike).where(LuckyStrike.tele_id == tele_id).values(purchased_strikes=LuckyStrike.purchased_strikes + 3))
            elif num == -1:
                await session.execute(update(LuckyStrike).where(and_(LuckyStrike.tele_id == tele_id, LuckyStrike.purchased_strikes > 0)).values(purchased_strikes=LuckyStrike.purchased_strikes - 1))
            await session.commit()

async def get_random_card(card_num: int, type: str):
    async with async_session() as session:
        res_cards = []
        for _ in range(card_num):
            if type == "random_card":
                rareness = generate_item_rarity("random_card")
            elif type == "lucky_strike":
                rareness = generate_item_rarity("lucky_strike")

            rareness = get_rareness_by_str(rareness)

            card_result = await session.execute(select(Card).where(Card.rareness == rareness))
            card_list = card_result.scalars().all()
            # print(card_list)
            try:
                # index = random.randint(0, len(card_list) - 1) if len(card_list) != 0 else 0
                # print(index)
                # res_cards.append(card_list[index])

                res_cards.append(random.choice(card_list))
            except:
                traceback.print_exc()
                return []
        return res_cards





