from pydantic import BaseModel


class ForgotPassword(BaseModel):
    username: str


class ChangePassword(BaseModel):
    token: str
    password: str
