import datetime
import json
import random
import sys
import ast
sys.path.append('/root/Offside-bot/TelegramBot')

from Databases.DB import *


async def main():
    async with async_session() as session:
        async with session.begin():

            # users
            data = []
            with open("Tables/users.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                date_string1 = i[4]
                date_string2 = i[7]

                date_format = "%Y-%m-%d %H:%M:%S.%f"

                try:
                    date_obj1 = datetime.datetime.strptime(date_string1, date_format)
                except:
                    try:
                        date_obj1 = datetime.datetime.strptime(date_string1, "%Y-%m-%d")
                    except:
                        date_obj1=None

                try:
                    date_obj2 = datetime.datetime.strptime(date_string2, date_format)
                except:
                    try:
                        date_obj2 = datetime.datetime.strptime(date_string2, "%Y-%m-%d")
                    except:
                        date_obj2=None

                ls = User(tele_id=int(i[0]) if i[0] != None else None,
                          card_num=int(i[1]) if i[1] != None else None,
                          card_rating=int(i[2]) if i[2] != None else None,
                          penalty_rating=int(i[3]),
                          register_at=date_obj1,
                          lk_message_id=int(i[5]) if i[5] != None else None,
                          transactions=int(i[6]),
                          free_card=date_obj2,
                          get_messages=int(i[8])
                          )

                session.add(ls)

            await session.commit()





    async with async_session() as session:
        async with session.begin():
            # lucky_strike
            data = []
            with open("Tables/lucky_strike.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                date_string = i[1]
                date_format = "%Y-%m-%d %H:%M:%S.%f"

                try:
                    date_obj = datetime.datetime.strptime(date_string, date_format)
                except:

                    try:
                        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                    except:
                        date_obj=None


                ls = LuckyStrike(tele_id=int(i[0]) if i[0] != None else None,
                                 free_strike=date_obj,
                                purchased_strikes=int(i[2]) if i[2] != None else None,
                                free_strikes=int(i[3])
                )

                session.add(ls)

            # cards
            data = []
            with open("Tables/cards.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                date_string1 = i[7]
                date_string2= i[8]

                date_format = "%Y-%m-%d %H:%M:%S.%f"

                try:
                    date_obj1 = datetime.datetime.strptime(date_string1, date_format)
                except:
                    try:
                        date_obj1 = datetime.datetime.strptime(date_string1, "%Y-%m-%d")
                    except:

                        date_obj1 = None

                try:
                    date_obj2 = datetime.datetime.strptime(date_string2, date_format)
                except:
                    try:
                        date_obj2 = datetime.datetime.strptime(date_string2, "%Y-%m-%d")
                    except:
                        date_obj2=None



                ls = Card(card_id = int(i[0]) if i[0] != None else None,
                        photo_id = i[1],
                        player_name = i[2],
                        player_nickname = i[3],
                        team = i[4],
                        rareness = i[5],
                        points = int(i[6]),
                        created_at = date_obj1,
                        updated_at = date_obj2
                                 )

                session.add(ls)

            # cards_of_user
            data = []
            with open("Tables/cards_of_user.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:

                ls = CardsOfUser(card_key=int(i[0]) if i[0] != None else None,
                          is_new=bool(i[3]),
                          tele_id=int(i[1]) if i[1] != None else None,
                          card_id=int(i[2]) if i[2] != None else None,
                          )

                session.add(ls)

            # check_promo
            data = []
            with open("Tables/check_promo.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                ls = CheckPromo(id=random.randint(1000000000,1000000000000),
                                 tele_id=int(i[0]) if i[0] != None else None,
                                 promo=i[1],
                                 )

                session.add(ls)

            # offers
            data = []
            with open("Tables/offers.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                ls = Offer(id=random.randint(1000000000, 1000000000000),
                                 tele_id1=int(i[0]) if i[0] != None else None,
                                 tele_id2=int(i[1]) if i[1] != None else None,
                                 agree1=bool(i[2]),
                                 agree2=bool(i[3]),
                                 card_id1=int(i[4]) if i[4] != None else None,
                                 card_id2=int(i[5]) if i[5] != None else None,
                                 )

                session.add(ls)

            # operations
            data = []
            with open("Tables/operations.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            used = []
            for i in data:
                if i[0] in used:
                    continue
                used.append(i[0])
                ls = Operation(operation_id=i[0],
                           operation_name=i[1],
                           user_id=int(i[2]) if i[2] != None else None,
                           finished=bool(i[3])
                           )

                session.add(ls)

            # packs
            data = []
            with open("Tables/packs.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                ls = Pack(buy_id=int(i[0]) if i[0] != None else None,
                               cost=int(i[1]) if i[1] != None else None,
                               name=str(i[2])
                               )

                session.add(ls)

            # promos
            data = []
            with open("Tables/promos.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                ls = Promo(promo_id=int(i[0]) if i[0] != None else None,
                               promo=i[1],
                               card_id=int(i[2]) if i[2] != None else None,
                               usages=str(i[3])
                               )

                session.add(ls)

            # spam
            data = []
            with open("Tables/spam.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                date_string = i[2]
                date_format = "%Y-%m-%d %H:%M:%S.%f"

                try:
                    date_obj = datetime.datetime.strptime(date_string, date_format)
                except:

                    try:
                        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                    except:
                        date_obj=None


                ls = Spam(user_id=int(i[0]) if i[0] != None else None,
                               msg_num=int(i[1]) if i[1] != None else None,
                               last_msg=date_obj,
                               banned=bool(i[3])
                               )

                session.add(ls)

            # admins
            data = []
            with open("Tables/admins.txt", "r") as file:
                for i in file:
                    data.append(ast.literal_eval(i.rstrip()))

            for i in data:
                ls = Admin(tele_id=int(i[0]) if i[0] != None else None)

                session.add(ls)

            await session.commit()

if __name__ == '__main__':
    asyncio.run(main())


