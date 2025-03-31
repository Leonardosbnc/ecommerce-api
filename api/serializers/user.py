from pydantic import BaseModel


class UserResponse(BaseModel):
    email: str
    username: str


class UserRequest(BaseModel):
    email: str
    username: str
    password: str
