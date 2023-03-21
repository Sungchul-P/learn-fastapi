from fastapi import FastAPI

from api import router as post_router
from database import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(post_router)
