from typing import Union

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    id: int
    title: str
    content: Union[str, None] = None


posts = []
next_post_id = 1


@app.post("/posts/")
async def create_post(post: Post):
    global next_post_id
    post.id = next_post_id
    next_post_id += 1
    posts.append(post)
    print(posts)
    return post


@app.get("/posts/{post_id}")
async def read_post(post_id: int):
    global posts
    post = next((p for p in posts if p.id == post_id), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@app.get("/posts/")
async def read_posts():
    global posts
    return {"posts": posts}
