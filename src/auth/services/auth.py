import os
from datetime import timedelta, datetime, UTC

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import User
from src.auth.schemas import TokenPairSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv("ALGORITHM")
USER_IDENTIFIER = 'user_id'

ACCESS_TOKEN_EXPIRE = os.getenv('ACCESS_TOKEN_EXPIRE')
REFRESH_TOKEN_EXPIRE = os.getenv('REFRESH_TOKEN_EXPIRE')


class TokenService:

    async def create_token_pair(self, user_id: int) -> TokenPairSchema:
        access_token = await self._create_jwt_token(
            {USER_IDENTIFIER: user_id, "type": "access"},
            timedelta(minutes=int(ACCESS_TOKEN_EXPIRE)),
        )

        refresh_token = await self._create_jwt_token(
            {USER_IDENTIFIER: user_id, "type": "refresh"},
            timedelta(hours=int(REFRESH_TOKEN_EXPIRE)),
        )

        return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> str:
        payload = await self._get_token_payload(refresh_token, 'refresh')

        return await self._create_jwt_token({USER_IDENTIFIER: payload[USER_IDENTIFIER], 'type': 'access'},
                                            timedelta(minutes=int(ACCESS_TOKEN_EXPIRE)))

    async def _create_jwt_token(self, data: dict, delta: timedelta) -> str:
        expire_delta = datetime.now(UTC) + delta
        data.update({'exp': expire_delta})
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def _get_token_payload(self, token: str, token_type: str) -> dict:
        try:
            payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail='Invalid token.')

        if payload.get('type') != token_type:
            raise HTTPException(status_code=401, detail='Invalid token.')
        if payload.get(USER_IDENTIFIER) is None:
            raise HTTPException(status_code=401, detail='Could not validate credentials')

        return payload

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               session: AsyncSession = Depends(get_session)) -> User:

        payload = await self._get_token_payload(token, 'access')
        try:
            query = select(User).where(User.id == payload[USER_IDENTIFIER])
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                raise HTTPException(status_code=404, detail='User not found.')
            return user
        except JWTError:
            raise HTTPException(status_code=401, detail='Could not validate credentials')

