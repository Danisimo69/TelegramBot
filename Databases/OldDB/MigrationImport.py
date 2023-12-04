import datetime
import json
import random
import sys
sys.path.append('/root/Offside-bot/TelegramBot')

from Databases.DB import *


async def main():
    async with async_session() as session:
        with session.begin():

            # users
            data = []
            with open("Tables/users.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                date_string1 = i[4]
                date_string2 = i[7]

                date_format = "%Y-%m-%d %H:%M:%S.%f"

                date_obj1 = datetime.datetime.strptime(date_string1, date_format)
                date_obj2 = datetime.datetime.strptime(date_string2, date_format)

                ls = User(tele_id=int(i[0]),
                          card_num=int(i[1]),
                          card_rating=int(i[2]),
                          penalty_rating=int(i[3]),
                          register_at=date_obj1,
                          lk_message_id=int(i[5]),
                          transactions=int(i[6]),
                          free_card=date_obj2,
                          get_messages=int(i[8])
                          )

                session.add(ls)

            # lucky_strike
            data = []
            with open("Tables/lucky_strike.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                date_string = i[1]
                date_format = "%Y-%m-%d %H:%M:%S.%f"

                date_obj = datetime.datetime.strptime(date_string, date_format)

                ls = LuckyStrike(tele_id=int(i[0]),
                                 free_strike=date_obj,
                                purchased_strikes=int(i[2]),
                                free_strikes=int(i[3])
                )

                session.add(ls)

            # cards
            data = []
            with open("Tables/cards.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                date_string1 = i[7]
                date_string2= i[8]

                date_format = "%Y-%m-%d %H:%M:%S.%f"

                date_obj1 = datetime.datetime.strptime(date_string1, date_format)
                date_obj2 = datetime.datetime.strptime(date_string2, date_format)


                ls = Card(card_id = int(i[0]),
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
                    data.append(json.loads(i.rstrip()))

            for i in file:

                ls = CardsOfUser(card_key=int(i[0]),
                          is_new=bool(i[3]),
                          tele_id=int(i[1]),
                          card_id=int(i[2]),
                          )

                session.add(ls)

            # check_promo
            data = []
            with open("Tables/check_promo.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = CheckPromo(id=random.randint(1000000000,1000000000000),
                                 tele_id=int(i[0]),
                                 promo=i[1],
                                 )

                session.add(ls)

            # offers
            data = []
            with open("Tables/offers.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = Offer(id=random.randint(1000000000, 1000000000000),
                                 tele_id1=int(i[0]),
                                 tele_id2=int(i[1]),
                                 agree1=bool(i[2]),
                                 agree2=bool(i[3]),
                                 card_id1=int(i[4]),
                                 card_id2=int(i[5]),
                                 )

                session.add(ls)

            # operations
            data = []
            with open("Tables/operations.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = Operation(operation_id=i[0],
                           operation_name=i[1],
                           user_id=int(i[2]),
                           finished=bool(i[3])
                           )

                session.add(ls)

            # packs
            data = []
            with open("Tables/packs.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = Pack(buy_id=int(i[0]),
                               cost=int(i[1]),
                               name=str(i[2])
                               )

                session.add(ls)

                    # penalties
                    # data = []
                    # with open("Tables/penalti.txt", "r") as file:
                    #     for i in file:
                    #         data.append(json.loads(i.rstrip()))
                    #
                    # for i in file:
                    #     date_string = i[1]
                    #     date_format = "%Y-%m-%d %H:%M:%S.%f"
                    #
                    #     date_obj = datetime.datetime.strptime(date_string, date_format)
                    #
                    #     ls = Penalty(id=random.randint(1000000000, 1000000000000),
                    #                user1_id=int(i[0]),
                    #                user2_id=int(i[1]),
                    #                turn=bool(i[2]),
                    #                def_status=bool(i[3]),
                    #                score1=int(i[4]),
                    #                score2=int(i[5]),
                    #                  last_kick=int(i[4]),
                    #                  turn1=int(i[5]),
                    #                  turn2=int(i[4]),
                    #
                    #                )
                    #
                    #     session.add(ls)

            # promos
            data = []
            with open("Tables/promos.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = Promo(promo_id=int(i[0]),
                               promo=i[1],
                               card_id=int(i[2]),
                               usages=str(i[3])
                               )

                session.add(ls)

            # spam
            data = []
            with open("Tables/spam.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                date_string = i[2]
                date_format = "%Y-%m-%d %H:%M:%S.%f"

                date_obj = datetime.datetime.strptime(date_string, date_format)

                ls = Spam(user_id=int(i[0]),
                               msg_num=int(i[1]),
                               last_msg=date_obj,
                               banned=bool(i[3])
                               )

                session.add(ls)

            # admins
            data = []
            with open("Tables/admins.txt", "r") as file:
                for i in file:
                    data.append(json.loads(i.rstrip()))

            for i in file:
                ls = Admin(tele_id=int(i[0]))

                session.add(ls)

            await session.commit()

if __name__ == '__main__':
    asyncio.run(main())


