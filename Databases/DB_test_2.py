import datetime
import sys

from sqlalchemy import select

sys.path.append('/root/Offside-bot/TelegramBot')

from Databases.DB import *


async def SpamClean():

    async with async_session() as session:
        spams = await session.execute(select(Spam))
        spams = spams.scalars().all()

        for i in spams:
            i.banned = False

        await session.commit()

async def ErrorLuckyStrike():

    async with async_session() as session:
        lucky_s = await session.execute(select(LuckyStrike).where(LuckyStrike.tele_id==942706258))
        lucky_s = lucky_s.scalar_one()

        free_strike_date = lucky_s.free_strike
        now = datetime.datetime.now()
        need_delta = datetime.timedelta(hours=4)
        remaining_time = need_delta - (
            now - free_strike_date) if lucky_s.free_strikes > 0 else datetime.timedelta(days=1) - (
            now - free_strike_date)

        print(lucky_s.tele_id, lucky_s.free_strike,
                lucky_s.purchased_strikes,
                lucky_s.free_strikes)
        print(now)
        print(need_delta)
        print(remaining_time)

if __name__ == '__main__':
    asyncio.run(ErrorLuckyStrike())



