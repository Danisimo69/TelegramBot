import uuid

from sqlalchemy import select, update, delete, or_, and_
import datetime

import random

from DB import *

async def create_game(tele_id1: int):
    async with async_session() as session:
        async with session.begin():
            new_game = Penalty(id=str(uuid.uuid4()), user1_id=tele_id1, turn=tele_id1, score1='', score2='', turn1='', turn2='')
            session.add(new_game)
            try:
                await session.commit()
                return 0
            except Exception as e:
                if "UNIQUE" in str(e):
                    return -1
                raise e

async def user_in_game(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where((Penalty.user1_id == tele_id) | (Penalty.user2_id == tele_id)))
        return game_result.scalar_one_or_none() is not None

async def insert_second_user(tele_id2: int, tele_id1: int):
    async with async_session() as session:
        async with session.begin():
            try:
                await session.execute(update(Penalty).where(Penalty.user1_id == tele_id1).values(user2_id=tele_id2))
                await session.commit()
                return 0
            except Exception as e:
                if "UNIQUE" in str(e):
                    return -1
                raise e

async def start_game(tele_id2: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Penalty).where(Penalty.user2_id == tele_id2).values(last_kick=datetime.datetime.now()))
            await session.commit()

async def check_delta_rating(tele_id1: int, tele_id2: int):
    async with async_session() as session:
        user1_result = await session.execute(select(User).where(User.tele_id == tele_id1))
        user1 = user1_result.scalar_one_or_none()
        user2_result = await session.execute(select(User).where(User.tele_id == tele_id2))
        user2 = user2_result.scalar_one_or_none()

        if user1 and user2:
            delta = abs(user1.mental_rating - user2.mental_rating)
            return delta >= 300
        return False

async def check_delta(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(Penalty.user1_id == tele_id))
        game = game_result.scalar_one_or_none()

        if game and game.last_kick:
            delta = datetime.datetime.now() - game.last_kick
            minute = datetime.timedelta(minutes=1)
            turn1, turn2 = int(game.turn1), int(game.turn2)
            if delta >= minute and turn1 == turn2 == 0:
                return [True, 0]
            if delta >= minute and turn1 == 0:
                return [True, game.user1_id]
            if delta >= minute and turn2 == 0:
                return [True, game.user2_id]
        return [False, False]

async def set_kick_time(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)).values(last_kick=datetime.datetime.now()))
            await session.commit()

async def place_turn_in_db(tele_id: int, num: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.turn1 == 0)).values(turn1=num))
            await session.execute(update(Penalty).where(or_(Penalty.user2_id == tele_id, Penalty.turn2 == 0)).values(turn2=num))
            await session.commit()

async def is_scored(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            game_result = await session.execute(select(Penalty).where(and_(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id), Penalty.turn1 != 0, Penalty.turn2 != 0)))
            game = game_result.scalar_one_or_none()
            if game is None:
                return [False, -1]

            if game.turn1 != game.turn2:

                if game.turn == game.user1_id:
                    await session.execute(
                        update(Penalty).where(Penalty.user1_id == game.turn).values(score1='1'))
                    keeper_id = game.user2_id

                else:
                    await session.execute(
                        update(Penalty).where(Penalty.user2_id == game.turn).values(score2='1'))
                    keeper_id = game.user1_id

                await session.execute(update(Penalty).where(Penalty.turn == game.turn).values(turn1='0',turn2='0'))
                await session.commit()


            else:

                if game.turn == game.user1_id:
                    await session.execute(
                        update(Penalty).where(Penalty.user1_id == game.turn).values(score1='0'))
                    keeper_id = game.user2_id

                else:
                    await session.execute(
                        update(Penalty).where(Penalty.user2_id == game.turn).values(score2='0'))
                    keeper_id = game.user1_id

                await session.execute(update(Penalty).where(Penalty.turn == game.turn).values(turn1='0', turn2='0'))
                await session.commit()

        return [True, game.turn, keeper_id]

async def is_finished(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
        game = game_result.scalar_one_or_none()
        if game and len(game.score1) > 5 or len(game.score2) > 5:
            return -1
        if game and len(game.score1) == len(game.score2) == 5:
            return True
        return False

async def is_kicker(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(Penalty.turn == tele_id))
        return game_result.scalar_one_or_none() is not None

async def get_kicker(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(or_(Penalty.user2_id == tele_id,Penalty.user1_id == tele_id)))
        game = game_result.scalar_one_or_none()
        return game.turn if game else None

async def change_kicker(keeper_id: int):
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(Penalty).where(or_(Penalty.user1_id == keeper_id, Penalty.user2_id == keeper_id)).values(turn=keeper_id))
            await session.commit()

async def get_score_str(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
        game = game_result.scalar_one_or_none()

        first_str = ""
        second_str = ""
        for score in game.score1:
            if score == "1":
                first_str += "⚽️"
            if score == "0":
                first_str += "❌"
        for score in game.score2:
            if score == "1":
                second_str += "⚽️"
            if score == "0":
                second_str += "❌"

        if len(game.score1) > len(game.score2):
            second_str += "\U0000231B"

        if game.user1_id == game.turn:
            return [first_str, second_str]
        else:
            return [second_str, first_str]

async def get_second_user(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
        game = game_result.scalar_one_or_none()
        return game.user2_id if game and game.user1_id == tele_id else game.user1_id if game else None

async def calc_result(tele_id: int):
    async with async_session() as session:
        game_result = await session.execute(select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
        game = game_result.scalar_one_or_none()

        score1_str = game.score1
        score2_str = game.score2
        score1 = 0
        score2 = 0
        for score in score1_str:
            if score != '0':
                score1 += 1
        for score in score2_str:
            if score != '0':
                score2 += 1
        if score1 > score2:
            return [1, game.user1_id, game.user2_id]
        elif score1 < score2:
            return [1, game.user2_id, game.user1_id]
        else:
            return [0, game.user1_id, game.user2_id]


async def finish_game(tele_id: int):
    result = await calc_result(tele_id)
    if result[0] == 0:
        return [0, result[1], result[2]]
    else:
        winner_id, loser_id = result[1], result[2]

        async with async_session() as session:
            async with session.begin():
                await session.execute(update(User).where(User.tele_id == winner_id).values(penalty_rating=User.penalty_rating + 25))
                await session.execute(update(User).where(and_(User.tele_id == loser_id, User.penalty_rating >= 25)).values(penalty_rating=User.penalty_rating - 25))
                await session.commit()

            return [1, winner_id, loser_id]

async def select_all_games():
    async with async_session() as session:
        games_result = await session.execute(select(Penalty))
        games = games_result.scalars().all()
        return games if games else None

async def destroy_game(tele_id: int):
    delta = await check_delta(tele_id)

    if delta and delta[0]:

        async with async_session() as session:
            async with session.begin():

                if delta[1] == 0:

                    await session.execute(delete(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
                    await session.commit()

                else:

                    await session.execute(update(User).where(and_(User.penalty_rating >= 25, User.tele_id == delta[1])).values(penalty_rating=User.penalty_rating - 25))

                    game_result = await session.execute(select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
                    game = game_result.scalar_one_or_none()

                    ans = game.user1_id
                    if game.user1_id != delta[1]:
                        await session.execute(
                            update(User).where(User.tele_id == game.user1_id).values(
                                penalty_rating=User.penalty_rating + 25))
                    else:

                        ans = game.user2_id

                        await session.execute(
                            update(User).where(User.tele_id == game.user2_id).values(
                                penalty_rating=User.penalty_rating + 25))

                    await session.commit()

            if delta[1] == 0:
                return [game.user1_id, game.user2_id, False]

            else:
                await delete_game(tele_id)
                return [ans, delta[1], True]

    else:
        return [0, 0]

async def delete_game(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            game_result = await session.execute(
                select(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
            game = game_result.scalar_one_or_none()

            await session.execute(delete(Penalty).where(or_(Penalty.user1_id == tele_id, Penalty.user2_id == tele_id)))
            await session.commit()

        return [game.user1_id, game.user2_id]



