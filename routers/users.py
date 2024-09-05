from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import PublicUsers, PrivateUsers
from routers.auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=4)


@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(PublicUsers).filter(PublicUsers.id == user.get("id")).first()


@router.put("/change-password/", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, db: db_dependency,
                          change_password_request: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(PrivateUsers).filter(PrivateUsers.id == user.get("id")).first()

    if not bcrypt_context.verify(change_password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    user_model.hashed_password = bcrypt_context.hash(change_password_request.new_password)
    db.add(user_model)
    db.commit()


@router.put("/update-phone-number/", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency,
                              phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(PrivateUsers).filter(PrivateUsers.id == user.get("id")).first()

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
