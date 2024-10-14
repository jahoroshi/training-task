import os

from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from src.auth.schemas import UserCreateSchema
from src.auth.services.repository import UserRepository

load_dotenv()

pwd_context = CryptContext(schemes=[os.getenv('PWD_ALGORITHMS')], deprecated='auto')


class PasswordHasher:

    @staticmethod
    async def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class UserService:

    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    async def create_user(self, data: UserCreateSchema, session: AsyncSession):
        user_dict = data.model_dump()
        user_dict['password'] = await self.password_hasher.hash_password(user_dict['password'])
        user = User(**user_dict)
        try:
            return await self.user_repo.add_user(user, session)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exist.")

    async def authenticate_user(self, credentials: HTTPBasicCredentials, session: AsyncSession) -> User:
        user = await self.user_repo.get_user_by_username(credentials.username, session)
        if not user:
            raise HTTPException(status_code=404, detail='User not found.')
        if not await self.password_hasher.verify_password(credentials.password, user.password):
            raise HTTPException(status_code=400, detail='Incorrect password.')
        return user

