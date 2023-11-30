from Databases.DB import *


async def AddAdmin():

    async with async_session() as session:

        admin = Admin(tele_id=649811235)

        session.add(admin)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(AddAdmin())



