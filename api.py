from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session
from starlette import status

from database import engine
from exceptions import NotAuthenticated
from model import Comment, Post, User
from service import (
    CommentCreate,
    CommentRead,
    CommentUpdate,
    PostCreate,
    PostRead,
    PostUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
    create_comment,
    create_post,
    create_user,
    delete_comment,
    delete_post,
    delete_user,
    get_current_user,
    login,
    logout,
    read_post,
    read_post_comments,
    read_posts,
    read_user,
    read_user_comments,
    read_user_posts,
    read_users,
    update_comment,
    update_post,
    update_user,
)

router = APIRouter()
security = HTTPBasic()


def get_session():
    with Session(engine) as session:
        yield session


def get_current_session(
    credentials: HTTPBasicCredentials = Depends(security), session: Session = Depends(get_session)
) -> Optional[Any]:
    username = credentials.username
    user, user_session = get_current_user(username, session)
    if not user or not user_session:
        raise NotAuthenticated
    user_session["user_id"] = user.id
    return user_session


@router.post("/users/login")
async def login_route(
    credentials: HTTPBasicCredentials = Depends(security), session: Session = Depends(get_session)
) -> dict[str, str]:
    return await login(credentials, session)


@router.post("/users/logout")
async def logout_route(current_session=Depends(get_current_session)) -> dict[str, str]:
    current_user_id = current_session["user_id"]

    return await logout(current_user_id)


@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user_route(user: UserCreate, session: Session = Depends(get_session)):
    return await create_user(user, session)


@router.get("/users/", status_code=status.HTTP_200_OK)
async def read_users_route(
    offset: int = 0, limit: int = Query(default=10), session: Session = Depends(get_session)
) -> List[User]:
    return await read_users(offset, limit, session)


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
async def read_user_route(user_id: str, session: Session = Depends(get_session)) -> User:
    return await read_user(user_id, session)


@router.get(
    "/users/{user_id}/posts", status_code=status.HTTP_200_OK, response_model=List[PostRead]
)
async def read_user_posts_route(
    user_id: str,
    page: int = 0,
    limit: int = Query(default=5),
    session: Session = Depends(get_session),
) -> List[Post]:
    offset = page * limit
    return await read_user_posts(user_id, offset, limit, session)


@router.get(
    "/users/{user_id}/comments", status_code=status.HTTP_200_OK, response_model=List[CommentRead]
)
async def read_user_comments_route(
    user_id: str,
    page: int = 0,
    limit: int = Query(default=5),
    session: Session = Depends(get_session),
) -> list[Comment]:
    offset = page * limit
    return await read_user_comments(user_id, offset, limit, session)


@router.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_route(
    user_id: str, user: UserUpdate, session: Session = Depends(get_session)
) -> User:
    return await update_user(user_id, user, session)


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_route(
    user_id: str, password: str, session: Session = Depends(get_session)
) -> dict[str, bool]:
    return await delete_user(user_id, password, session)


@router.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post_route(post: PostCreate, session: Session = Depends(get_session)) -> Post:
    return await create_post(post, session)


@router.get("/posts/", status_code=status.HTTP_200_OK)
async def read_posts_route(
    offset: int = 0, limit: int = Query(default=100), session: Session = Depends(get_session)
) -> List[Post]:
    return await read_posts(offset, limit, session)


@router.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post_route(post_id: int, session: Session = Depends(get_session)) -> Post:
    return await read_post(post_id, session)


@router.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post_route(
    post_id: int, post: PostUpdate, session: Session = Depends(get_session)
) -> Post:
    return await update_post(post_id, post, session)


@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post_route(
    post_id: int, author: str, session: Session = Depends(get_session)
) -> dict[str, bool]:
    return await delete_post(post_id, author, session)


@router.post("/posts/{post_id}/comments/", status_code=status.HTTP_201_CREATED)
async def create_comment_route(
    post_id: int, comment: CommentCreate, session: Session = Depends(get_session)
) -> Comment:
    return await create_comment(post_id, comment, session)


@router.get(
    "/posts/{post_id}/comments/", status_code=status.HTTP_200_OK, response_model=List[CommentRead]
)
async def read_post_comments_route(
    post_id: int,
    page: int = 0,
    limit: int = Query(default=5),
    session: Session = Depends(get_session),
) -> List[Comment]:
    offset = page * limit
    return await read_post_comments(post_id, offset, limit, session)


@router.put("/posts/{post_id}/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def update_comment_route(
    post_id: int, comment_id: int, comment: CommentUpdate, session: Session = Depends(get_session)
) -> Comment:
    return await update_comment(post_id, comment_id, comment, session)


@router.delete("/posts/{post_id}/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment_route(
    comment_id: int, author: str, session: Session = Depends(get_session)
) -> dict[str, bool]:
    return await delete_comment(comment_id, author, session)
