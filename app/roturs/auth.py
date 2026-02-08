from fastapi import Response, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, schema, utils, oauth2
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=schema.Token)
async def login(user_credential: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(database.User).filter(database.User.email == user_credential.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    print(user_credential.password, user.password)

    if not utils.verify_password(user_credential.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    #create token and return it to the user in a real application
    token = oauth2.create_access_token(data={"user_id": user.id})
    return schema.Token(access_token=token, token_type="bearer")
