from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(..., max_length=256)


class UserSchema(UserBaseSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=1, max_length=50)


class UserCredentialSchema(BaseModel):
    username: str
    password: str


class AccessTokenSchema(BaseModel):
    access_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenPairSchema(AccessTokenSchema, RefreshTokenSchema):
    pass
