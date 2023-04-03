from typing import Optional

from sqlmodel import Field, SQLModel


class PostBase(SQLModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)  # 부모 클래스의 __init_subclass__ 호출
        cls.table = kwargs.get("table")  # 'table' 인자를 받아 클래스 속성에 저장

    title: str
    content: Optional[str]
    author: str = Field(index=True)


class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PostCreate(PostBase):
    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Tutorial",
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author": "Anonymous",
            }
        }

    pass


class PostRead(PostBase):
    id: int


class PostUpdate(SQLModel):
    title: Optional[str]
    content: Optional[str]
    author: str
