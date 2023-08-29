import pytest
from sqlmodel import Session, SQLModel, create_engine

import api
from main import app

DATABASE_URL = "sqlite:///test_posts.db"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)
SQLModel.metadata.drop_all(engine)


def test_db_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
def override_dependencies():
    SQLModel.metadata.create_all(engine)

    original_dependency = app.dependency_overrides.get(api.get_session)
    app.dependency_overrides[api.get_session] = test_db_session
    yield
    if original_dependency:
        app.dependency_overrides[api.get_session] = original_dependency
    else:
        del app.dependency_overrides[api.get_session]

    SQLModel.metadata.drop_all(engine)
