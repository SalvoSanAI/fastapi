from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from random import randrange
import logging
import time
from app.schema import *
from app.database import get_db, Post, User
from app import oauth2
import logging


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/")
async def get_posts(db: Session = Depends(get_db)):
    """Get all posts from the database using ORM."""
    try:
        posts = db.query(Post).all()
        return {"data": [PostResponse.model_validate(post) for post in posts]}
    except Exception as error:
        logger.error(f"Error fetching posts from database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching posts from database"
        )

@router.get("/latest")
async def get_latest_post(db: Session = Depends(get_db)):
    """Get the latest post from the database using ORM."""
    try:
        latest_post = db.query(Post).order_by(Post.id.desc()).first()
        if latest_post:
            return {"data": PostResponse.model_validate(latest_post)}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts found"
            )
    except Exception as error:
        logger.error(f"Error fetching latest post from database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching latest post from database"
        )

@router.get("/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID from the database using ORM."""
    try:
        post = db.query(Post).filter(Post.id == id).first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id: {id} was not found"
            )
        return {"data": PostResponse.model_validate(post)}
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error fetching post {id} from database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching post from database"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    """Create a new post in the database using ORM."""
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post data is required"
        )

    try:
        
        print(current_user.email)  # Accessing email to ensure current_user is valid

        new_post = Post(**post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return PostResponse.model_validate(new_post)
    except Exception as error:
        db.rollback()
        logger.error(f"Error creating post in database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post in database"
        )



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    """Delete a post from the database using ORM."""
    try:
        post = db.query(Post).filter(Post.id == id).first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id: {id} does not exist"
            )
        db.delete(post)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.error(f"Error deleting post {id} from database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting post from database"
        )

@router.put("/{id}")
async def update_post(id: int, post: PostCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    """Update an existing post in the database using ORM."""
    try:
        existing_post = db.query(Post).filter(Post.id == id).first()
        if existing_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"post with id: {id} does not exist"
            )
        for key, value in post.dict().items():
            setattr(existing_post, key, value)
        db.commit()
        db.refresh(existing_post)
        return {"data": PostResponse.model_validate(existing_post)}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.error(f"Error updating post {id} in database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating post in database"
        )