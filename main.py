from typing import Optional, List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    id: Optional[int]
    title: str
    content: Optional[str]
    author: str

    class Config:
        schema_extra = {
            "example": {
                "title": "FastAPI Tutorial",
                "content": "Learn how to build APIs with FastAPI and Python.",
                "author": "beginner"
            }
        }
        exclude = {'id'}


posts = []
next_post_id = 1


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    global next_post_id
    post.id = next_post_id
    next_post_id += 1
    posts.append(post)
    return post


@app.get("/posts/{post_id}")
async def read_post(post_id: int):
    global posts
    post = next((p for p in posts if p.id == post_id), None)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
        )
    return post


@app.get("/posts/")
async def read_posts():
    global posts
    return {"posts": posts}


@app.put("/posts/{post_id}")
async def update_post(post_id: int, new_post: Post):
    global posts
    post = next((p for p in posts if p.id == post_id), None)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
        )

    if post.author != new_post.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 수정할 수 있습니다"
        )

    post.title = new_post.title
    post.content = new_post.content

    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, author: str):
    global posts
    for index, post in enumerate(posts):
        if post.id == post_id:
            if post.author != author:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="게시글 작성자만 삭제할 수 있습니다"
                )
            del posts[index]
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다"
    )
