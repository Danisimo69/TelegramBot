import datetime as dt
import sqlite3 as sq
# убран один импорт


def create_game(tele_id1):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                '''INSERT INTO penalti (user1_id, turn, score1, score2, turn1, turn2) VALUES(?, ?, '', '', 0, 0)''',
                (tele_id1, tele_id1,))
            connection.commit()
            return 0
    except sq.Error as e:
        print("Ошибка при работе с дб")
        if "UNIQUE" in str(e):
            return -1
        print(e)


def user_in_game(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? or user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            if res is None:
                return False
            else:
                return True
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def insert_second_user(tele_id2, tele_id1):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''UPDATE penalti SET user2_id = ? WHERE user1_id = ?''', (tele_id2, tele_id1))
            connection.commit()
            return 0
    except sq.Error as e:
        print("Ошибка при работе с дб")
        if "UNIQUE" in str(e):
            return -1
        print(e)


def start_game(tele_id2):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''UPDATE penalti SET last_kick = ? WHERE user2_id = ?''',
                           (str(dt.datetime.now()).split(".")[0], tele_id2))
            connection.commit()
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


# функция проверки разницы рейтинга между игроками
def check_delta_rating(tele_id1, tele_id2):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM users WHERE tele_id = ?''', (tele_id1,))
            user1 = cursor.fetchone()
            cursor.execute('''SELECT * FROM users WHERE tele_id = ?''', (tele_id2,))
            user2 = cursor.fetchone()
            delta = abs(user1[3] - user2[3])
            if delta >= 300:
                return True
            else:
                return False
    except sq.Error as e:
        print("Ошибка при работе с бд")
        print(e)


def check_delta(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ?''', (tele_id,))
            res = cursor.fetchone()
            # добавлена эта проверка
            if res is None:
                return [False, False]
            if res[5] is not None:
                kick_str = res[5].split(" ")
                kick_date = kick_str[0].split("-")
                k_time = kick_str[1].split(":")
                kick_time = dt.datetime(year=int(kick_date[0]), month=int(kick_date[1]), day=int(kick_date[2]),
                                        hour=int(k_time[0]), minute=int(k_time[1]), second=int(k_time[2]))
                cur_time = dt.datetime.now()
                # изменены все строчки ниже в этой функции
                delta = cur_time - kick_time
                minute = dt.timedelta(minutes=1)
                turn1 = int(res[6])
                turn2 = int(res[7])
                if delta >= minute and turn1 == turn2 == 0:
                    return [True, 0]
                if delta >= minute and turn1 == 0:
                    return [True, res[0]]
                if delta >= minute and turn2 == 0:
                    return [True, res[1]]
            return [False, False]
            # до этого момента
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def set_kick_time(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''UPDATE penalti SET last_kick = ? WHERE user1_id = ? OR user2_id = ?''',
                           (str(dt.datetime.now()).split(".")[0], tele_id, tele_id))
            connection.commit()
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def place_turn_in_db(tele_id, num):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''UPDATE penalti SET turn1 = ? WHERE user1_id = ? AND turn1 = 0''', (num, tele_id))
            cursor.execute('''UPDATE penalti SET turn2 = ? WHERE user2_id = ? AND turn2 = 0''', (num, tele_id))
            connection.commit()
    except sq.Error as e:
        print("Ошибка при работе с бд")
        print(e)


def is_scored(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE (user1_id = ? OR user2_id = ?) AND turn1 != 0 AND turn2 != 0''',
                           (tele_id, tele_id))
            res = cursor.fetchone()
            if res is None:
                return [False, -1]
            if res[6] != res[7]:
                if res[2] == res[0]:
                    cursor.execute('''UPDATE penalti SET score1 = score1 || ? WHERE user1_id = ?''',
                                   ('1', res[2]))
                    keeper_id = res[1]
                else:
                    cursor.execute('''UPDATE penalti SET score2 = score2 || ? WHERE user2_id = ?''',
                                   ('1', res[2]))
                    keeper_id = res[0]
                connection.commit()
                cursor.execute('''UPDATE penalti SET turn1 = 0, turn2 = 0 WHERE turn = ?''', (res[2],))
                return [True, res[2], keeper_id]
            if res[6] == res[7]:
                if res[2] == res[0]:
                    cursor.execute('''UPDATE penalti SET score1 = score1 || ? WHERE user1_id = ?''',
                                   ('0', res[2]))
                    keeper_id = res[1]
                else:
                    cursor.execute('''UPDATE penalti SET score2 = score2 || ? WHERE user2_id = ?''',
                                   ('0', res[2]))
                    keeper_id = res[0]
                # добавлена строка ниже
                connection.commit()
                cursor.execute('''UPDATE penalti SET turn1 = 0, turn2 = 0 WHERE turn = ?''', (res[2],))
                # добавлена строка ниже
                connection.commit()
                return [False, res[2], keeper_id]
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def is_finished(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            if len(res[3]) > 5 or len(res[4]) > 5:
                return -1
            if len(res[3]) == len(res[4]) == 5:
                return True
            else:
                return False
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def is_kicker(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE turn = ?''', (tele_id,))
            if cursor.fetchone() is not None:
                return True
            else:
                return False
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def get_kicker(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user2_id = ? OR user1_id = ?''', (tele_id, tele_id))
            return cursor.fetchone()[2]
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def change_kicker(keeper_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''UPDATE penalti SET turn = ? WHERE user1_id = ? OR user2_id = ?''', (keeper_id, keeper_id, keeper_id))
            connection.commit()
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def get_score_str(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            first_str = ""
            second_str = ""
            for score in res[3]:
                if score == "1":
                    first_str += "⚽️"
                if score == "0":
                    first_str += "❌"
            for score in res[4]:
                if score == "1":
                    second_str += "⚽️"
                if score == "0":
                    second_str += "❌"
            if len(res[3]) > len(res[4]):
                second_str += "\U0000231B"
            if res[0] == res[2]:
                return [first_str, second_str]
            else:
                return [second_str, first_str]
    except sq.Error as e:
        print("Ошибка при работе с бд")
        print(e)


def get_second_user(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            if res[0] != tele_id:
                return res[0]
            if res[1] != tele_id:
                return res[1]
    except sq.Error as e:
        print("Ошибка при работе с бд")
        print(e)


def calc_result(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            score1_str = res[3]
            score2_str = res[4]
            score1 = 0
            score2 = 0
            for score in score1_str:
                if score != '0':
                    score1 += 1
            for score in score2_str:
                if score != '0':
                    score2 += 1
            if score1 > score2:
                return [1, res[0], res[1]]
            elif score1 < score2:
                return [1, res[1], res[0]]
            else:
                return [0, res[0], res[1]]
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)


def finish_game(tele_id):
    result = calc_result(tele_id)
    if result[0] == 0:
        return [0, result[1], result[2]]
    else:
        winner_id = result[1]
        loser_id = result[2]
        try:
            with sq.connect("card-bot.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''UPDATE users SET penalti_rating = penalti_rating + 25 WHERE tele_id = ?''',
                               (winner_id,))
                cursor.execute(
                    '''UPDATE users SET penalti_rating = penalti_rating - 25 WHERE penalti_rating >= 25 AND tele_id = ?''',
                    (loser_id,))
                connection.commit()
                return [1, winner_id, loser_id]
        except sq.Error as e:
            print("Ошибка при работе с дб")
            print(e)


def select_all_games():
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti''')
            res = cursor.fetchall()
            if len(res) == 0:
                return None
            else:
                return res
    except sq.Error as e:
        print("Ошибка при работе с бд")
        print(e)


def destroy_game(tele_id):
    delta = check_delta(tele_id)
    if delta is not None and delta[0]:
        try:
            with sq.connect("card-bot.db") as connection:
                cursor = connection.cursor()
                # добавлена следующая проверка ниже
                if delta[1] == 0:
                    cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''',
                                   (tele_id, tele_id))
                    res = cursor.fetchone()
                    cursor.execute('''DELETE FROM penalti WHERE user1_id = ?''', (res[0],))
                    connection.commit()
                    return [res[0], res[1], False]
                cursor.execute(
                    '''UPDATE users SET penalti_rating = penalti_rating - 25 WHERE penalti_rating >= 25 AND tele_id = ?''',
                    (delta[1],))
                cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
                res = cursor.fetchone()
                ans = res[0]
                if res[0] != delta[1]:
                    cursor.execute(
                        '''UPDATE users SET penalti_rating = penalti_rating + 25 WHERE tele_id = ?''',
                        (res[0],))
                else:
                    ans = res[1]
                    cursor.execute(
                        '''UPDATE users SET penalti_rating = penalti_rating + 25 WHERE tele_id = ?''',
                        (res[1],))
                connection.commit()
                delete_game(tele_id)
                # return был изменен
                return [ans, delta[1], True]
        except sq.Error as e:
            print("Ошибка при работе с бд")
            print(e)
    else:
        return [0, 0]


def delete_game(tele_id):
    try:
        with sq.connect("card-bot.db") as connection:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            res = cursor.fetchone()
            cursor.execute('''DELETE FROM penalti WHERE user1_id = ? OR user2_id = ?''', (tele_id, tele_id))
            connection.commit()
            return [res[0], res[1]]
    except sq.Error as e:
        print("Ошибка при работе с дб")
        print(e)
