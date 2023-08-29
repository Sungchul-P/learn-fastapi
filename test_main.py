import uuid
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlmodel import Field, Session, select

from conftest import engine
from main import app
from model import Comment, Post, User

client = TestClient(app)


class UserPayload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password: str = "Password123"
    nickname: str = "Anonymous"
    role: str = "member"


class PostPayload(BaseModel):
    title: str = "FastAPI Tutorial"
    content: str = "Learn how to build APIs with FastAPI and Python."
    author_id: str


class CommentPayload(BaseModel):
    content: str = "Learn how to build APIs with FastAPI and Python."
    author_id: str


@pytest.fixture(scope="function")
def user_payload() -> UserPayload:
    return UserPayload()


@pytest.fixture(scope="function")
def post_payload(user_payload) -> PostPayload:
    return PostPayload(author_id=user_payload.id)


@pytest.fixture(scope="function")
def comment_payload(post_payload) -> CommentPayload:
    return CommentPayload(author_id=post_payload.author_id)


def test_create_user(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    # When
    response = client.post("/users/", json=user)

    # Then
    assert response.status_code == 201
    api_user = response.json()
    assert api_user["id"] == user["id"]
    assert api_user["password"] == user["password"]
    assert api_user["nickname"] == user["nickname"]
    assert api_user["role"] == user["role"]

    with Session(engine) as session:
        db_user: Optional[User] = session.get(User, user["id"])
        assert db_user is not None
        assert db_user.id == user["id"]
        assert db_user.password == user["password"]
        assert db_user.nickname == user["nickname"]
        assert db_user.role == user["role"]


def test_create_user_invalid_input():
    # Given
    # When
    response = client.post("/users/", json={"nickname": "Anonymous"})

    # Then
    assert response.status_code == 422


def test_read_users(user_payload: UserPayload):
    # Given
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # When
    response = client.get("/users/")

    # Then
    assert response.status_code == 200

    api_users = response.json()
    with Session(engine) as session:
        db_users = session.exec(select(User)).all()

    """
    created_at 날짜 형식 변환
    - API 호출 : '2023-08-29T07:14:54.783739'
    - DB 직접 호출 : datetime.datetime(2023, 8, 29, 7, 14, 54, 783739)
    """
    db_users_dict = [
        {**user.dict(), "created_at": user.created_at.isoformat()} for user in db_users
    ]
    assert api_users == db_users_dict


def test_read_user(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # When
    response = client.get(f"/users/{user['id']}")

    # Then
    assert response.status_code == 200
    api_user = response.json()
    assert api_user["id"] == user["id"]
    assert api_user["password"] == user["password"]
    assert api_user["nickname"] == user["nickname"]


def test_read_user_not_found():
    # Given
    # When
    response = client.get("/users/999999")

    # Then
    assert response.status_code == 404


def test_update_user(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    update_user = user.copy()
    update_user["nickname"] = "UpdatedNickname"

    # When
    response = client.put(f"/users/{user['id']}", json=update_user)

    # Then
    assert response.status_code == 200
    updated_api_user = response.json()
    assert updated_api_user["id"] == update_user["id"]
    assert updated_api_user["password"] == update_user["password"]
    assert updated_api_user["nickname"] == update_user["nickname"]
    assert updated_api_user["role"] == update_user["role"]

    with Session(engine) as session:
        db_updated_user: Optional[User] = session.get(User, update_user["id"])
        assert db_updated_user is not None
        assert db_updated_user.id == update_user["id"]
        assert db_updated_user.password == update_user["password"]
        assert db_updated_user.nickname == update_user["nickname"]
        assert db_updated_user.role == update_user["role"]


def test_update_user_not_found(user_payload: UserPayload):
    # Given
    user = user_payload.dict()

    # When
    response = client.put("/users/999999", json=user)

    # Then
    assert response.status_code == 404


def test_update_user_invalid_password(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    invalid_user = user.copy()
    invalid_user["password"] = "InvalidPassword"

    # When
    response = client.put(f"/users/{invalid_user['id']}", json=invalid_user)

    # Then
    assert response.status_code == 403


def test_delete_user(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # When
    response = client.delete(f"/users/{user['id']}", params={"password": user["password"]})

    # Then
    assert response.status_code == 200


def test_delete_user_invalid_password(user_payload: UserPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # When
    response = client.delete(f"/users/{user['id']}", params={"password": "InvalidPassword"})

    # Then
    assert response.status_code == 403


def test_create_post(post_payload: PostPayload):
    # Given
    post = post_payload.dict()

    # When
    response = client.post("/posts/", json=post)

    # Then
    assert response.status_code == 201
    api_post = response.json()
    assert api_post["author_id"] == post["author_id"]
    assert api_post["title"] == post["title"]
    assert api_post["content"] == post["content"]

    with Session(engine) as session:
        db_post: Optional[Post] = session.get(Post, api_post["id"])
        assert db_post is not None
        assert db_post.id == api_post["id"]
        assert db_post.author_id == post["author_id"]
        assert db_post.title == post["title"]
        assert db_post.content == post["content"]


def test_read_posts(post_payload: PostPayload):
    # Given
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.get("/posts/")

    # Then
    assert response.status_code == 200

    api_posts = response.json()
    with Session(engine) as session:
        db_posts = session.exec(select(Post)).all()

    db_posts_dict = [post.dict() for post in db_posts]
    assert api_posts == db_posts_dict


def test_read_post(post_payload: PostPayload):
    # Given
    post = post_payload.dict()
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.get("/posts/1")

    # Then
    assert response.status_code == 200
    api_post = response.json()
    assert api_post["author_id"] == post["author_id"]
    assert api_post["title"] == post["title"]
    assert api_post["content"] == post["content"]


def test_read_post_not_found():
    # Given
    # When
    response = client.get("/posts/999999")

    # Then
    assert response.status_code == 404


def test_update_post(post_payload: PostPayload):
    # Given
    post = post_payload.dict()
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    update_post = post.copy()
    update_post["title"] = "UpdatedTitle"

    # When
    response = client.put("/posts/1", json=update_post)

    # Then
    assert response.status_code == 200
    updated_api_post = response.json()
    assert updated_api_post["author_id"] == update_post["author_id"]
    assert updated_api_post["title"] == update_post["title"]
    assert updated_api_post["content"] == update_post["content"]

    with Session(engine) as session:
        db_updated_post: Optional[Post] = session.get(Post, updated_api_post["id"])
        assert db_updated_post is not None
        assert db_updated_post.id == updated_api_post["id"]
        assert db_updated_post.author_id == update_post["author_id"]
        assert db_updated_post.title == update_post["title"]
        assert db_updated_post.content == update_post["content"]


def test_update_post_not_found(post_payload: PostPayload):
    # Given
    post = post_payload.dict()

    # When
    response = client.put("/posts/999999", json=post)

    # Then
    assert response.status_code == 404


def test_update_post_invalid_author(post_payload: PostPayload):
    # Given
    post = post_payload.dict()
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    invalid_post = post.copy()
    invalid_post["author_id"] = "InvalidAuthor"

    # When
    response = client.put("/posts/1", json=invalid_post)

    # Then
    assert response.status_code == 403


def test_read_user_posts(user_payload: UserPayload, post_payload: PostPayload):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.get(f"/users/{user['id']}/posts")

    # Then
    assert response.status_code == 200

    api_posts = response.json()
    with Session(engine) as session:
        query = select(Post).where(Post.author_id == user["id"])
        db_posts_by_user = session.exec(query).all()

    db_posts_dict = [post.dict() for post in db_posts_by_user]
    assert api_posts == db_posts_dict


def test_delete_post(post_payload: PostPayload):
    # Given
    post = post_payload.dict()
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.delete("/posts/1", params={"author": post["author_id"]})

    # Then
    assert response.status_code == 200


def test_delete_post_invalid_author(post_payload: PostPayload):
    # Given
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.delete("/posts/1", params={"author": "InvalidAuthor"})

    # Then
    assert response.status_code == 403


def test_create_comment(comment_payload: CommentPayload):
    # Given
    comment = comment_payload.dict()

    # When
    response = client.post("/posts/1/comments/", json=comment)

    # Then
    assert response.status_code == 201
    api_comment = response.json()
    assert api_comment["author_id"] == comment["author_id"]
    assert api_comment["content"] == comment["content"]

    with Session(engine) as session:
        db_comment: Optional[Comment] = session.get(Comment, api_comment["id"])
        assert db_comment is not None
        assert db_comment.id == api_comment["id"]
        assert db_comment.author_id == comment["author_id"]
        assert db_comment.content == comment["content"]


def test_read_post_comments(post_payload: PostPayload, comment_payload: CommentPayload):
    # Given
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        db_comment = Comment(post_id=1, **comment_payload.dict())
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)

    # When
    response = client.get("/posts/1/comments/")

    # Then
    assert response.status_code == 200

    api_comments = response.json()
    with Session(engine) as session:
        query = select(Comment).where(Comment.post_id == 1)
        db_comments_by_post = session.exec(query).all()

    """
    created_at 날짜 형식 변환
    - API 호출 : '2023-08-29T07:14:54.783739'
    - DB 직접 호출 : datetime.datetime(2023, 8, 29, 7, 14, 54, 783739)
    """
    db_comments_dict = [
        {**comment.dict(), "created_at": comment.created_at.isoformat()}
        for comment in db_comments_by_post
    ]
    assert api_comments == db_comments_dict


def test_read_user_comments(
    user_payload: UserPayload, post_payload: PostPayload, comment_payload: CommentPayload
):
    # Given
    user = user_payload.dict()
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        db_comment = Comment(post_id=1, **comment_payload.dict())
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)

    # When
    response = client.get(f"/users/{user['id']}/comments")

    # Then
    assert response.status_code == 200

    api_comments = response.json()
    with Session(engine) as session:
        query = select(Comment).where(Comment.author_id == user["id"])
        db_comments_by_user = session.exec(query).all()

    """
    created_at 날짜 형식 변환
    - API 호출 : '2023-08-29T07:14:54.783739'
    - DB 직접 호출 : datetime.datetime(2023, 8, 29, 7, 14, 54, 783739)
    """
    db_comments_dict = [
        {**comment.dict(), "created_at": comment.created_at.isoformat()}
        for comment in db_comments_by_user
    ]
    assert api_comments == db_comments_dict


def test_update_comment(
    user_payload: UserPayload, post_payload: PostPayload, comment_payload: CommentPayload
):
    # Given
    user = user_payload.dict()
    comment = comment_payload.dict()
    comment["password"] = user["password"]

    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        db_comment = Comment(post_id=1, **comment_payload.dict())
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)

    update_comment = comment.copy()
    update_comment["content"] = "UpdatedContent"

    # When
    response = client.put("/posts/1/comments/1", json=update_comment)

    # Then
    assert response.status_code == 200
    updated_api_comment = response.json()
    assert updated_api_comment["author_id"] == update_comment["author_id"]
    assert updated_api_comment["content"] == update_comment["content"]

    with Session(engine) as session:
        db_updated_comment: Optional[Comment] = session.get(Comment, updated_api_comment["id"])
        assert db_updated_comment is not None
        assert db_updated_comment.id == updated_api_comment["id"]
        assert db_updated_comment.author_id == update_comment["author_id"]
        assert db_updated_comment.content == update_comment["content"]


def test_update_comment_not_found(
    user_payload: UserPayload, post_payload: PostPayload, comment_payload: CommentPayload
):
    # Given
    user = user_payload.dict()
    comment = comment_payload.dict()
    comment["password"] = user["password"]
    with Session(engine) as session:
        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

    # When
    response = client.put("/posts/1/comments/999999", json=comment)

    # Then
    assert response.status_code == 404


def test_update_comment_invalid_password(
    user_payload: UserPayload, post_payload: PostPayload, comment_payload: CommentPayload
):
    # Given
    user = user_payload.dict()
    comment = comment_payload.dict()
    comment["password"] = user["password"]
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        db_comment = Comment(post_id=1, **comment_payload.dict())
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)

    invalid_comment = comment.copy()
    invalid_comment["password"] = "InvalidPassword"

    # When
    response = client.put("/posts/1/comments/1", json=invalid_comment)

    # Then
    assert response.status_code == 403


def test_delete_comment(
    user_payload: UserPayload, post_payload: PostPayload, comment_payload: CommentPayload
):
    # Given
    user = user_payload.dict()
    comment = comment_payload.dict()
    comment["password"] = user["password"]
    with Session(engine) as session:
        db_user = User.from_orm(user_payload)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        db_post = Post.from_orm(post_payload)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        db_comment = Comment(post_id=1, **comment_payload.dict())
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)

    # When
    response = client.delete("/posts/1/comments/1", params={"author": comment["author_id"]})

    # Then
    assert response.status_code == 200
