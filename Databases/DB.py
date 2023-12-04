import asyncio

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, NullPool, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base

# Настройка базы данных

engine = create_async_engine('postgresql+asyncpg://postgres:Vanilla9797@localhost/TG_db_test', poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class LuckyStrike(Base):
    __tablename__ = 'lucky_strike'
    tele_id = Column(BigInteger, primary_key=True)
    free_strike = Column(DateTime)
    purchased_strikes = Column(BigInteger, default=0)
    free_strikes = Column(BigInteger, default=2)

class Admin(Base):
    __tablename__ = 'admins'
    tele_id = Column(BigInteger, primary_key=True)

class Card(Base):
    __tablename__ = 'cards'
    card_id = Column(BigInteger, primary_key=True)
    photo_id = Column(Text)
    player_name = Column(String(255))
    player_nickname = Column(String(255))
    team = Column(String(255))
    rareness = Column(BigInteger)
    points = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CardsOfUser(Base):
    __tablename__ = 'cards_of_user'

    card_key = Column(BigInteger, primary_key=True)
    is_new = Column(Boolean)

    tele_id = Column(BigInteger, ForeignKey('users.tele_id'))
    card_id = Column(BigInteger, ForeignKey('cards.card_id'))


class CheckPromo(Base):
    __tablename__ = 'check_promo'
    id = Column(BigInteger, primary_key=True)
    tele_id = Column(BigInteger)
    promo = Column(Text)

class Offer(Base):
    __tablename__ = 'offers'
    id = Column(BigInteger, primary_key=True)

    tele_id1 = Column(BigInteger)
    tele_id2 = Column(BigInteger)
    agree1 = Column(Boolean)
    agree2 = Column(Boolean)

    card_id1 = Column(BigInteger)
    card_id2 = Column(BigInteger)

class Operation(Base):
    __tablename__ = 'operations'
    operation_id = Column(Text, primary_key=True)
    operation_name = Column(Text)
    user_id = Column(BigInteger)
    finished = Column(Boolean, default=False)

class Pack(Base):
    __tablename__ = 'packs'
    buy_id = Column(BigInteger, primary_key=True)
    cost = Column(BigInteger)
    name = Column(Text)

class Penalty(Base):
    __tablename__ = 'penalties'

    id = Column(String(255), primary_key=True)

    user1_id = Column(BigInteger)
    user2_id = Column(BigInteger)
    turn = Column(BigInteger)
    def_status = Column(Boolean, default=False)
    score1 = Column(Text)
    score2 = Column(Text)
    last_kick = Column(DateTime)
    turn1 = Column(Text)
    turn2 = Column(Text)

class Promo(Base):
    __tablename__ = 'promos'
    promo_id = Column(BigInteger, primary_key=True)
    promo = Column(Text)
    card_id = Column(BigInteger, ForeignKey('cards.card_id'))
    usages = Column(Text, default="INF")

class Spam(Base):
    __tablename__ = 'spam'
    user_id = Column(BigInteger, primary_key=True)

    msg_num = Column(BigInteger, default=1)
    last_msg = Column(DateTime)
    banned = Column(Boolean, default=False)

class User(Base):
    __tablename__ = 'users'
    tele_id = Column(BigInteger, primary_key=True)
    card_num = Column(BigInteger)
    card_rating = Column(BigInteger)
    penalty_rating = Column(BigInteger)
    register_at = Column(DateTime)
    lk_message_id = Column(BigInteger)
    transactions = Column(BigInteger, default=0)
    free_card = Column(DateTime)
    get_messages = Column(BigInteger, default=0)

async def async_main():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def async_drop():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

if __name__ == '__main__':

    asyncio.run(async_drop())
    asyncio.run(async_main())