import sys

from sqlalchemy import select, or_

sys.path.append('/root/Offside-bot/TelegramBot')

from Databases.DB import *


# async def AddAdmin():
#
#     async with async_session() as session:
#
#         for i in admins:
#             admin = Admin(tele_id=i)
#
#             session.add(admin)
#
#         await session.commit()

async def AddPacks():

    async with async_session() as session:

        mod = Pack(buy_id=1,
                   cost=5,
                   name="3 рандомных карточки")
        session.add(mod)

        mod = Pack(buy_id=2,
                   cost=10,
                   name="5 рандомных карточек")
        session.add(mod)

        mod = Pack(buy_id=3,
                   cost=15,
                   name="10 рандомных карточек")
        session.add(mod)

        mod = Pack(buy_id=4,
                   cost=20,
                   name="50 рандомных карточек")
        session.add(mod)

        mod = Pack(buy_id=5,
                   cost=10,
                   name="Легендарный набор")
        session.add(mod)

        mod = Pack(buy_id=10,
                   cost=10,
                   name="Удары")
        session.add(mod)

        await session.commit()

async def PromoClean():

    async with async_session() as session:
        promos = await session.execute(select(Promo))
        promos = promos.scalars().all()

        for i in promos:
            await session.delete(i)

        promos = await session.execute(select(CheckPromo))
        promos = promos.scalars().all()

        for i in promos:
            await session.delete(i)

        await session.commit()

async def OfferClean():
    async with async_session() as session:
        offers = await session.execute(select(Offer).where(or_(Offer.tele_id1 == 942706258, Offer.tele_id2 == 942706258)))
        offers = offers.scalars().all()

        for i in offers:
            await session.delete(i)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(AddPacks())



