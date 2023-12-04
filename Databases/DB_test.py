import sys

sys.path.append('/root/Offside-bot/TelegramBot')
from main_config import admins

from Databases.DB import *


async def AddAdmin():

    async with async_session() as session:

        for i in admins:
            admin = Admin(tele_id=i)

            session.add(admin)

        await session.commit()

async def AddPacks():

    async with async_session() as session:

        mod = Pack(buy_id=1,
                   cost=5,
                   name="Одна карточка")
        session.add(mod)

        mod = Pack(buy_id=2,
                   cost=10,
                   name="Три карточки")
        session.add(mod)

        mod = Pack(buy_id=3,
                   cost=15,
                   name="Пять карточкек")
        session.add(mod)

        mod = Pack(buy_id=4,
                   cost=10,
                   name="Удары")
        session.add(mod)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(AddAdmin())



