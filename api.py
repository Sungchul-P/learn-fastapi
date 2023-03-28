from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from starlette import status

from database import engine
from domain import PostCreate, PostUpdate
from service import create_post, delete_post, read_post, read_posts, update_post

router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post_route(post: PostCreate, session: Session = Depends(get_session)):
    return await create_post(post, session)


@router.get("/posts/")
async def read_posts_route(
    offset: int = 0,
    limit: int = Query(default=100),
    session: Session = Depends(get_session),
):
    return await read_posts(offset, limit, session)


@router.get("/posts/{post_id}")
async def read_post_route(post_id: int, session: Session = Depends(get_session)):
    return await read_post(post_id, session)


@router.put("/posts/{post_id}")
async def update_post_route(post_id: int, post: PostUpdate, session: Session = Depends(get_session)):
    return await update_post(post_id, post, session)


@router.delete("/posts/{post_id}")
async def delete_post_route(post_id: int, author: str, session: Session = Depends(get_session)):
    return await delete_post(post_id, author, session)
