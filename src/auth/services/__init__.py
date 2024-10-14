from src.auth.services.auth import TokenService
from src.auth.services.management import PasswordHasher, UserService
from src.auth.services.repository import UserRepository

password_hasher = PasswordHasher()
user_repository = UserRepository()

user_service = UserService(user_repository, password_hasher)
token_service = TokenService()
