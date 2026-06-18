from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False

    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError, InvalidHash:
        return False
