import uuid

import pytest
from fastapi.testclient import TestClient

import api
from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "id": str(uuid.uuid4()),
        "password": "Password123",
        "nickname": "Anonymous",
        "role": "member",
    }


@pytest.fixture(scope="module")
def post(user):
    return {
        "title": "FastAPI Tutorial",
        "content": "Learn how to build APIs with FastAPI and Python.",
        "author_id": user["id"],
    }


@pytest.fixture(scope="module")
def comment(post):
    return {
        "content": "Learn how to build APIs with FastAPI and Python.",
        "author_id": post["author_id"],
    }


def test_create_user(override_dependencies, user):
    response = client.post("/users/", json=user)
    assert response.status_code == 201
    assert response.json()["id"] == user["id"]
    assert response.json()["password"] == user["password"]
    assert response.json()["nickname"] == user["nickname"]
    assert response.json()["role"] == user["role"]


def test_create_user_invalid_input(override_dependencies):
    response = client.post("/users/", json={"nickname": "Anonymous"})
    assert response.status_code == 422


def test_read_users(override_dependencies):
    response = client.get("/users/")
    assert response.status_code == 200


def test_read_user(override_dependencies, user):
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["password"] == user["password"]
    assert response.json()["nickname"] == user["nickname"]


def test_read_user_not_found(override_dependencies):
    response = client.get("/users/999999")
    assert response.status_code == 404


def test_update_user(override_dependencies, user):
    response = client.put(f"/users/{user['id']}", json=user)
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["password"] == user["password"]
    assert response.json()["nickname"] == user["nickname"]
    assert response.json()["role"] == user["role"]


def test_update_user_not_found(override_dependencies, user):
    response = client.put("/users/999999", json=user)
    assert response.status_code == 404


def test_update_user_invalid_password(override_dependencies, user):
    invalid_user = user.copy()
    invalid_user["password"] = "InvalidPassword"
    response = client.put(f"/users/{invalid_user['id']}", json=invalid_user)
    assert response.status_code == 403


def test_create_post(override_dependencies, post):
    response = client.post("/posts/", json=post)
    assert response.status_code == 201
    assert response.json()["author_id"] == post["author_id"]
    assert response.json()["title"] == post["title"]
    assert response.json()["content"] == post["content"]


def test_read_posts(override_dependencies):
    response = client.get("/posts/")
    assert response.status_code == 200


def test_read_post(override_dependencies, post):
    response = client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["author_id"] == post["author_id"]
    assert response.json()["title"] == post["title"]
    assert response.json()["content"] == post["content"]


def test_read_post_not_found(override_dependencies):
    response = client.get("/posts/999999")
    assert response.status_code == 404


def test_update_post(override_dependencies, post):
    response = client.put("/posts/1", json=post)
    assert response.status_code == 200
    assert response.json()["author_id"] == post["author_id"]
    assert response.json()["title"] == post["title"]
    assert response.json()["content"] == post["content"]


def test_update_post_not_found(override_dependencies, post):
    response = client.put("/posts/999999", json=post)
    assert response.status_code == 404


def test_update_post_invalid_author(override_dependencies, post):
    invalid_post = post.copy()
    invalid_post["author_id"] = "InvalidAuthor"
    response = client.put("/posts/1", json=invalid_post)
    assert response.status_code == 403


def test_create_comment(override_dependencies, comment):
    response = client.post("/posts/1/comments/", json=comment)
    assert response.status_code == 201
    assert response.json()["author_id"] == comment["author_id"]
    assert response.json()["content"] == comment["content"]


def test_read_post_comments(override_dependencies):
    response = client.get("/posts/1/comments/")
    assert response.status_code == 200


def test_read_user_comments(override_dependencies, user):
    response = client.get(f"/users/{user['id']}/comments")
    assert response.status_code == 200


def test_read_user_posts(override_dependencies, user):
    response = client.get(f"/users/{user['id']}/comments")
    assert response.status_code == 200


def test_update_comment(override_dependencies, comment, user):
    comment["password"] = user["password"]
    response = client.put("/posts/1/comments/1", json=comment)
    assert response.status_code == 200
    assert response.json()["author_id"] == user["id"]
    assert response.json()["content"] == comment["content"]


def test_update_comment_not_found(override_dependencies, comment):
    response = client.put("/posts/1/comments/999999", json=comment)
    assert response.status_code == 404


def test_update_comment_invalid_password(override_dependencies, comment):
    invalid_comment = comment.copy()
    invalid_comment["password"] = "InvalidPassword"
    response = client.put("/posts/1/comments/1", json=invalid_comment)
    assert response.status_code == 403


def test_delete_comment(override_dependencies, comment):
    response = client.delete("/posts/1/comments/1", params={"author": comment["author_id"]})
    assert response.status_code == 200


def test_delete_post_invalid_author(override_dependencies, post):
    response = client.delete("/posts/1", params={"author": "InvalidAuthor"})
    assert response.status_code == 403


def test_delete_post(override_dependencies, post):
    response = client.delete("/posts/1", params={"author": post["author_id"]})
    assert response.status_code == 200


def test_delete_user_invalid_password(override_dependencies, user):
    response = client.delete(f"/users/{user['id']}", params={"password": "InvalidPassword"})
    assert response.status_code == 403


def test_delete_user(override_dependencies, user):
    response = client.delete(f"/users/{user['id']}", params={"password": user["password"]})
    assert response.status_code == 200
