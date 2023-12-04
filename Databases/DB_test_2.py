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

if __name__ == '__main__':
    asyncio.run(SpamClean())



