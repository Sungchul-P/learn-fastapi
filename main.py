from typing import Optional, List

from fastapi import FastAPI, HTTPException, status, Depends, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select


class PostBase(SQLModel):
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
                "author": "Anonymous"
            }
        }
    pass


class PostRead(PostBase):
    id: int


class PostUpdate(SQLModel):
    title: Optional[str]
    content: Optional[str]
    author: str


DATABASE_URL = "sqlite:///posts.db"

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/posts/", status_code=status.HTTP_201_CREATED, response_model=PostRead)
async def create_post(post: PostCreate, session: Session = Depends(get_session)):
    db_post = Post.from_orm(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[PostRead])
async def read_posts(offset: int = 0, limit: int = Query(default=100), session: Session = Depends(get_session)):
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


@app.get("/posts/{post_id}", response_model=PostRead)
async def read_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
        )
    return post


@app.put("/posts/{post_id}", response_model=PostRead)
async def update_post(post_id: int, post: PostUpdate, session: Session = Depends(get_session)):
    db_post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
        )

    if post.author != db_post.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다"
        )
    post_data = post.dict(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, author: str, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
        )

    if post.author != author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다"
        )
    session.delete(post)
    session.commit()
    return {"ok": True}
