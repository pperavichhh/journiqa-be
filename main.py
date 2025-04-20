from fastapi import Depends, FastAPI

from dependencies import get_query_token, get_token_header
from internal import admin
from routers import users

app = FastAPI()

app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}