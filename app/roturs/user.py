from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from random import randrange
import logging
import time
from app.schema import *
from app.database import get_db, User as Userdb
from ..utils import hash_password, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
) 

@router.get("/{id}")
async def get_user(id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID from the database using ORM."""
    try:
        user = db.query(Userdb).filter(Userdb.id == id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id: {id} was not found"
            )
        return {"data": User.model_validate(user)}
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error fetching user {id} from database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user from database"     
        )
    
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user in the database using ORM."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User data is required"
        )

    try:
        hashed_password = hash_password(user.password)
        user.password = hashed_password

        new_user = User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponse.model_validate(new_user)
    except Exception as error:
        db.rollback()
        print(f"Error creating user in database: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user in database: {error}"
        )    
