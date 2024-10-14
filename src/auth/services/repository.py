from typing import Sequence
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User



class UserRepository:

    @staticmethod
    async def add_user(user: User, session: AsyncSession) -> User:
        session.add(user)
        await session.commit()
        return user

    @staticmethod
    async def get_user_by_username(username: str, session: AsyncSession) -> User:
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()