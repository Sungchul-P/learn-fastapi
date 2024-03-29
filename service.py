import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi.security import HTTPBasicCredentials
from sqlmodel import Field, Session, SQLModel, select

from exceptions import (
    CommentAuthorizationFailedException,
    CommentCreationFailedException,
    CommentNotFoundException,
    NotAuthenticated,
    PostAuthorizationFailedException,
    PostCreationFailedException,
    PostNotFoundException,
    UserAuthorizationFailedException,
    UserCreationFailedException,
    UserNotFoundException,
    UserSessionNotFoundException,
)
from model import Comment, Post, Role, User


class UserCreate(SQLModel):
    id: str
    password: str
    nickname: Optional[str]
    role: Optional[Role]

    class Config:
        schema_extra = {
            "example": {
                "id": "user123",
                "password": "Password123",
                "nickname": "Anonymous",
                "role": Role.MEMBER,
            }
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


async def create_user(user: UserCreate, session: Session) -> User:
    try:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValueError as e:
        print(str(e))
        raise UserCreationFailedException(user.nickname)
    return db_user


async def read_users(offset: int, limit: int, session: Session) -> List[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


async def read_user(user_id: str, session: Session) -> User:
    user = get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundException
    return user


async def read_user_posts(user_id: str, offset: int, limit: int, session: Session) -> List[Post]:
    return await get_posts_by_user(user_id, offset, limit, session)


async def read_user_comments(
    user_id: str, offset: int, limit: int, session: Session
) -> List[Comment]:
    return await get_comments_by_user(user_id, offset, limit, session)


async def update_user(user_id: str, user: UserUpdate, session: Session) -> User:
    db_user: Optional[User] = get_user_by_id(user_id, session)
    if not db_user:
        raise UserNotFoundException

    if user.password != db_user.password:  # type: ignore
        raise UserAuthorizationFailedException
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


async def delete_user(user_id: str, password: str, session: Session) -> dict[str, bool]:
    user = get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundException

    if user.password != password:  # type: ignore
        raise UserAuthorizationFailedException
    session.delete(user)
    session.commit()
    return {"ok": True}


def get_post_by_id(post_id: int, session: Session) -> Optional[Post]:
    return session.get(Post, post_id)


async def create_post(post: PostCreate, session: Session) -> Post:
    try:
        db_post = Post.from_orm(post)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
    except ValueError as e:
        print(str(e))
        raise PostCreationFailedException(post.title)
    return db_post


async def read_posts(offset: int, limit: int, session: Session) -> List[Post]:
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


async def read_post(post_id: int, session: Session) -> Post:
    post = get_post_by_id(post_id, session)
    if not post:
        raise PostNotFoundException(post_id)
    return post


async def update_post(post_id: int, post: PostUpdate, session: Session) -> Post:
    db_post: Optional[Post] = get_post_by_id(post_id, session)
    if not db_post:
        raise PostNotFoundException(post_id)

    if post.author_id != db_post.author_id:  # type: ignore
        raise PostAuthorizationFailedException(post.author_id)
    post_data = post.dict(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


async def delete_post(post_id: int, author_id: str, session: Session) -> dict[str, bool]:
    post = get_post_by_id(post_id, session)
    if not post:
        raise PostNotFoundException(post_id)

    if post.author_id != author_id:  # type: ignore
        raise PostAuthorizationFailedException(post.author_id)
    session.delete(post)
    session.commit()
    return {"ok": True}


async def create_comment(post_id: int, comment: CommentCreate, session: Session) -> Comment:
    try:
        db_comment = Comment(post_id=post_id, **comment.dict())
        db_comment.post_id = post_id
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)
    except ValueError as e:
        print(str(e))
        raise CommentCreationFailedException(post_id)
    return db_comment


async def read_post_comments(
    post_id: int, offset: int, limit: int, session: Session
) -> List[Comment]:
    return await get_comments_by_post(post_id, offset, limit, session)


async def update_comment(
    post_id: int, comment_id: int, comment: CommentUpdate, session: Session
) -> Comment:
    db_comment: Optional[Comment] = session.get(Comment, comment_id)
    if not db_comment:
        raise CommentNotFoundException(comment_id)

    if post_id != db_comment.post_id:
        raise CommentNotFoundException(comment_id)
    elif comment.author_id != db_comment.author_id or comment.password != db_comment.user.password:
        raise CommentAuthorizationFailedException(comment.author_id)
    comment_data = comment.dict(exclude_unset=True, exclude={"password"})
    for key, value in comment_data.items():
        setattr(db_comment, key, value)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


async def delete_comment(comment_id: int, author_id: str, session: Session) -> dict[str, bool]:
    comment: Optional[Comment] = session.get(Comment, comment_id)
    if not comment:
        raise CommentNotFoundException(comment_id)

    if comment.author_id != author_id:
        raise CommentAuthorizationFailedException(author_id)
    session.delete(comment)
    session.commit()
    return {"ok": True}


user_sessions: Dict[str, Any] = {}


def get_current_user(username: str, session: Session) -> tuple[User, Optional[Any]]:
    user_session = user_sessions.get(username)
    if user_session and user_session["expire_date"] > datetime.now():
        user: Optional[User] = get_user_by_id(username, session)
        if user:
            return user, user_session

    raise NotAuthenticated


async def login(credentials: HTTPBasicCredentials, session: Session) -> dict[str, str]:
    user: Optional[User] = await read_user(credentials.username, session)

    if not user or user.password != credentials.password:
        raise UserAuthorizationFailedException

    user_session = user_sessions.get(credentials.username)
    if not user_session:
        user_session = {
            "session_id": secrets.token_hex(16),
            "expire_date": datetime.now() + timedelta(days=1),
        }
        user_sessions[credentials.username] = user_session
    else:
        user_session["expire_date"] = datetime.now() + timedelta(days=1)

    return {"message": f"{user.id} 로그인 성공!"}


async def logout(user_id: str) -> dict[str, str]:
    user_session = user_sessions.get(user_id)
    if user_session:
        del user_sessions[user_id]
        return {"message": f"{user_id} 로그아웃 성공."}
    else:
        raise UserSessionNotFoundException
