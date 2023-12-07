from sqlalchemy import select
import datetime
from Databases.DB import *

async def check_spam(tele_id: int):
    async with async_session() as session:
        async with session.begin():
            spam_result = await session.execute(select(Spam).where(Spam.user_id == tele_id))
            spam_record = spam_result.scalar_one_or_none()
            now_time = datetime.datetime.now()

            if spam_record == None:
                new_spam = Spam(user_id=tele_id, last_msg=now_time)
                session.add(new_spam)
                await session.commit()
                return False

            if spam_record.banned:
                return True

            if spam_record.msg_num > 1:
                spam_record.banned = True
                spam_record.last_msg = now_time
                await session.commit()
                return True

            else:
                spam_record.msg_num += 1
                spam_record.last_msg = now_time
                await session.commit()
                return False



async def unban_users():
    async with async_session() as session:
        async with session.begin():
            spammers_result = await session.execute(select(Spam))
            spammers_list = spammers_result.scalars().all()

            now_time = datetime.datetime.now()
            need_delta = datetime.timedelta(seconds=30)

            for spammer in spammers_list:
                if now_time - spammer.last_msg > need_delta or '-' in str(now_time - spammer.last_msg):
                    await session.delete(spammer)

            await session.commit()

