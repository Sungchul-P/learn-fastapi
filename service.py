from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Field, Session, SQLModel, select

from model import Comment, Post, User


class UserCreate(SQLModel):
    id: str
    password: str
    nickname: Optional[str]

    class Config:
        schema_extra = {
            "example": {"id": "user123", "password": "Password123", "nickname": "Anonymous"}
        }


class UserRead(SQLModel):
    id: str
    password: str
    nickname: Optional[str]
    created_at: datetime


class UserUpdate(SQLModel):
    password: str
    nickname: Optional[str]


class PostCreate(SQLModel):
    title: str
    content: Optional[str]
    author_id: str

    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Tutorial",
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author_id": "user123",
            }
        }


class PostRead(SQLModel):
    id: int
    title: str
    content: Optional[str]
    author_id: str = Field(index=True)


class PostUpdate(SQLModel):
    title: Optional[str]
    content: Optional[str]
    author_id: str


class CommentCreate(SQLModel):
    content: Optional[str]
    author_id: str
    post_id: int

    class Config:
        schema_extra = {
            "example": {
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author_id": "user123",
            }
        }


class CommentRead(SQLModel):
    id: int
    author_id: str
    post_id: int
    content: Optional[str]
    created_at: datetime


class CommentUpdate(SQLModel):
    content: Optional[str]
    author_id: str
    post_id: int
    password: str

    class Config:
        schema_extra = {
            "example": {
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author_id": "user123",
                "password": "Password123",
            }
        }


def get_user_by_id(user_id: str, session: Session) -> Optional[User]:
    return session.get(User, user_id)


def raise_user_not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")


async def get_posts_by_user(user_id: str, offset: int, limit: int, session: Session) -> List[Post]:
    query = select(Post).where(Post.author_id == user_id).offset(offset).limit(limit)
    posts = session.exec(query).all()
    return posts


async def get_comments_by_user(
    user_id: str, offset: int, limit: int, session: Session
) -> List[Comment]:
    query = select(Comment).where(Comment.author_id == user_id).offset(offset).limit(limit)
    comment = session.exec(query).all()
    return comment


async def get_comments_by_post(
    post_id: int, offset: int, limit: int, session: Session
) -> List[Comment]:
    query = select(Comment).where(Comment.post_id == post_id).offset(offset).limit(limit)
    comment = session.exec(query).all()
    return comment


async def create_user(user: UserCreate, session: Session):
    try:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_user


async def read_users(offset: int, limit: int, session: Session):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


async def read_user(user_id: str, session: Session):
    user = get_user_by_id(user_id, session)
    if not user:
        raise_user_not_found()
    return user


async def read_user_posts(user_id: str, offset: int, limit: int, session: Session):
    return await get_posts_by_user(user_id, offset, limit, session)


async def read_user_comments(user_id: str, offset: int, limit: int, session: Session):
    return await get_comments_by_user(user_id, offset, limit, session)


async def update_user(user_id: str, user: UserUpdate, session: Session):
    db_user: Optional[User] = get_user_by_id(user_id, session)
    if not db_user:
        raise_user_not_found()

    if user.password != db_user.password:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 틀렸습니다")
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


async def delete_user(user_id: str, password: str, session: Session):
    user = get_user_by_id(user_id, session)
    if not user:
        raise_user_not_found()

    if user.password != password:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 틀렸습니다")
    session.delete(user)
    session.commit()
    return {"ok": True}


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

    if post.author_id != db_post.author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    post_data = post.dict(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


async def delete_post(post_id: int, author_id: str, session: Session):
    post = get_post_by_id(post_id, session)
    if not post:
        raise_post_not_found()

    if post.author_id != author_id:  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    session.delete(post)
    session.commit()
    return {"ok": True}


async def create_comment(comment: CommentCreate, session: Session):
    db_comment = Comment.from_orm(comment)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


async def read_post_comments(post_id: int, offset: int, limit: int, session: Session):
    return await get_comments_by_post(post_id, offset, limit, session)


async def update_comment(comment_id: int, comment: CommentUpdate, session: Session):
    db_comment: Optional[Comment] = session.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다")

    if comment.password != db_comment.user.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 틀렸습니다")
    comment_data = comment.dict(exclude_unset=True)
    for key, value in comment_data.items():
        setattr(db_comment, key, value)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


async def delete_comment(comment_id: int, author_id: str, session: Session):
    comment: Optional[Comment] = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글을 찾을 수 없습니다")

    if comment.author_id != author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="댓글 작성자만 삭제할 수 있습니다")
    session.delete(comment)
    session.commit()
    return {"ok": True}
