"""Security utilities"""

import bcrypt

from pydantic_core import core_schema


def verify_password(plain_password, hashed_password) -> bool:
    """Verifies a hash against a password"""
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def get_password_hash(password) -> str:
    """Generates a hash from plain text"""
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    ).decode("utf8")


class HashedPassword(str):
    """Takes a plain text password and hashes it.
    use this as a field in your SQLModel
    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _, handler
    ) -> core_schema.CoreSchema:
        def validate(v):
            if not isinstance(v, str):
                raise TypeError("string required")

            hashed_password = get_password_hash(v)
            # you could also return a string here which would mean model.password
            # would be a string, pydantic won't care but you could end up with some
            # confusion since the value's type won't match the type annotation
            # exactly
            return cls(hashed_password)

        return core_schema.no_info_after_validator_function(
            validate, handler(str)
        )
