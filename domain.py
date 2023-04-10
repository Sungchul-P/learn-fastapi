import re
from datetime import datetime
from typing import List, Optional

from pydantic import validator
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):  # type: ignore
    id: str = Field(primary_key=True)
    posts: List["Post"] = Relationship(back_populates="user")
    password: str = Field()
    nickname: Optional[str] = Field(max_length=20, index=True)
    created_at: datetime = Field(default=datetime.utcnow())

    @validator("password")
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        if not re.search(r"[A-Z]", password):
            raise ValueError("비밀번호에는 최소 1개의 대문자가 포함되어야 합니다.")

        return password


class Post(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str]
    author_id: Optional[str] = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="posts")
