from typing import List

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from starlette import status

from database import engine
from service import (
    PostCreate,
    PostRead,
    PostUpdate,
    UserCreate,
    UserUpdate,
    create_post,
    create_user,
    delete_post,
    delete_user,
    read_post,
    read_posts,
    read_user_posts,
    read_users,
    update_post,
    update_user,
)

router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user_route(user: UserCreate, session: Session = Depends(get_session)):
    return await create_user(user, session)


@router.get("/users/")
async def read_users_route(
    offset: int = 0, limit: int = Query(default=10), session: Session = Depends(get_session)
):
    return await read_users(offset, limit, session)


@router.get("/users/posts", response_model=List[PostRead])
async def read_user_posts_route(
    user_id: str,
    page: int = 0,
    limit: int = Query(default=5),
    session: Session = Depends(get_session),
):
    offset = page * limit
    return await read_user_posts(user_id, offset, limit, session)


@router.put("/users/{user_id}")
async def update_user_route(
    user_id: str, user: UserUpdate, session: Session = Depends(get_session)
):
    return await update_user(user_id, user, session)


@router.delete("/users/{user_id}")
async def delete_user_route(user_id: str, password: str, session: Session = Depends(get_session)):
    return await delete_user(user_id, password, session)


@router.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post_route(post: PostCreate, session: Session = Depends(get_session)):
    return await create_post(post, session)


@router.get("/posts/")
async def read_posts_route(
    offset: int = 0, limit: int = Query(default=100), session: Session = Depends(get_session)
):
    return await read_posts(offset, limit, session)


@router.get("/posts/{post_id}")
async def read_post_route(post_id: int, session: Session = Depends(get_session)):
    return await read_post(post_id, session)


@router.put("/posts/{post_id}")
async def update_post_route(
    post_id: int, post: PostUpdate, session: Session = Depends(get_session)
):
    return await update_post(post_id, post, session)


@router.delete("/posts/{post_id}")
async def delete_post_route(post_id: int, author: str, session: Session = Depends(get_session)):
    return await delete_post(post_id, author, session)
