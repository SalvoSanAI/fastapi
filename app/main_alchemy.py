from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional
from random import randrange
import logging
import time
from .roturs import post, user, auth
from .config import settings

app = FastAPI(version="1.0.0.0", title="Posts API with ORM", description="A simple Posts API using SQLAlchemy ORM")



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "title of post 2", "content": "content of post 2", "id": 2}]



app.include_router(router=post.router)  
app.include_router(router=user.router)
app.include_router(router=auth.router)

@app.get("/")
async def get_default():
    return {"data": "Server is running"}

   