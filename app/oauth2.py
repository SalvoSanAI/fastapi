from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import time
from . import schema, database
from sqlalchemy.orm import Session
from .config import settings


#Secret key to encode and decode JWT tokens
SECRET_KEY = settings.secret_key
#Algorithm used to sign the JWT tokens
ALGORITHM = settings.algorithm
#Exiration time for the token in seconds (e.g., 30 minutes)
ACCESS_TOKEN_EXPIRE_SECONDS = settings.access_token_expire_seconds  # 30 minutes

out2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict):
    """Create a JWT access token with the given data and expiration time."""
    to_encode = data.copy()
    # Set the expiration time for the token
    expire = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    
    to_encode.update({"exp": expire})
    # Encode the token using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """Verify a JWT access token and return the decoded data if valid."""
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise JWTError("Invalid token: user_id not found")
        
        return schema.TokenData(id=id)
    except JWTError:
        # If the token is invalid or expired, raise an error
        raise credentials_exception
    

def get_current_user(token: str = Depends(out2_schema), db: Session = Depends(database.get_db)):
    """Get the current user from the JWT access token."""
    try:
        token_data = verify_access_token(token, credentials_exception=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,   
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ))

        user = db.query(database.User).filter(database.User.id == token_data.id).first()

        return user
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )