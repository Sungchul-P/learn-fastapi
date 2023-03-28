from fastapi import HTTPException, status
from sqlmodel import Session, select

from domain import Post, PostCreate, PostUpdate


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
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")
    return post


async def update_post(post_id: int, post: PostUpdate, session: Session):
    db_post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    if post.author != db_post.author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    post_data = post.dict(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


async def delete_post(post_id: int, author: str, session: Session):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    if post.author != author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다")
    session.delete(post)
    session.commit()
    return {"ok": True}
