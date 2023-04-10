from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Field, Session, SQLModel, select

from domain import Post


class PostCreate(SQLModel):
    title: str
    content: Optional[str]
    author: str = Field(index=True)

    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Tutorial",
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author": "Anonymous",
            }
        }


class PostRead(SQLModel):
    id: int
    title: str
    content: Optional[str]
    author: str = Field(index=True)  # type: ignore


class PostUpdate(SQLModel):
    title: Optional[str]
    content: Optional[str]
    author: str  # type: ignore


def get_post_by_id(post_id: int, session: Session) -> Optional[Post]:
    return session.get(Post, post_id)


def raise_post_not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")


async def create_post(post: PostCreate, session: Session):
    db_post = Post.from_orm(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


async def read_posts(offset: int, limit: int, session: Session):
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


async def read_post(post_id: int, session: Session):
    post = get_post_by_id(post_id, session)
    if not post:
        raise_post_not_found()
    return post


async def update_post(post_id: int, post: PostUpdate, session: Session):
    db_post: Optional[Post] = get_post_by_id(post_id, session)
    if not db_post:
        raise_post_not_found()

    if post.author != db_post.author:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    post_data = post.dict(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


async def delete_post(post_id: int, author: str, session: Session):
    post = get_post_by_id(post_id, session)
    if not post:
        raise_post_not_found()

    if post.author != author:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    session.delete(post)
    session.commit()
    return {"ok": True}
