from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from database import get_session
from src.auth.schemas import UserSchema, UserCreateSchema, TokenPairSchema, AccessTokenSchema, RefreshTokenSchema, \
    UserCredentialSchema
from src.auth.services import user_service, token_service

security = HTTPBasic()

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.post(
    '/registration',
    response_model=UserSchema,
    description="Регистрирует нового пользователя.",
    responses={
        201: {"description": "Пользователь успешно зарегистрирован."},
        400: {"description": "Некорректные данные или пользователь уже существует."},
    }
)
async def add_user(user: UserCreateSchema, session=Depends(get_session)):
    return await user_service.create_user(user, session)


@router.post(
    '/token',
    response_model=TokenPairSchema,
    description="Получение пары токенов по логину и паролю.",
    responses={
        200: {"description": "Токены успешно сгенерированы."},
        400: {"description": "Неверные учетные данные пользователя."},
    }
)
async def get_token_pair(user_data: UserCredentialSchema, session=Depends(get_session)):
    credentials = HTTPBasicCredentials(username=user_data.username, password=user_data.password)
    user = await user_service.authenticate_user(credentials, session)
    return await token_service.create_token_pair(user_id=user.id)


@router.post(
    '/token/refresh',
    response_model=AccessTokenSchema,
    description="Обновляет access токен с использованием refresh токена.",
    responses={
        200: {"description": "Токен успешно обновлен."},
        401: {"description": "Некорректный refresh токен."},
    }
)
async def refresh_token(token: RefreshTokenSchema):
    return AccessTokenSchema(access_token=await token_service.refresh_access_token(token.refresh_token))
