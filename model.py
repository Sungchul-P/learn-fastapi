import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import validator
from sqlmodel import Field, Relationship, SQLModel


class Role(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"


class User(SQLModel, table=True):  # type: ignore
    id: str = Field(primary_key=True)
    posts: List["Post"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")
    password: str = Field()
    nickname: Optional[str] = Field(max_length=20, index=True)
    role: Role = Field(default=Role.MEMBER, max_length=20)
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
    author_id: str = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")


class Comment(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: str = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="comments")
    post_id: int = Field(foreign_key="post.id")
    post: Post = Relationship(back_populates="comments")
    content: Optional[str]
    created_at: datetime = Field(default=datetime.utcnow())
