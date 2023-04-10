from typing import Optional

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str]
    author: str = Field(index=True)
