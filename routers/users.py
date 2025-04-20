from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.users import get_db
from models.users import UserDB
from schema.users import UserCreate, UserResponse, UserUpdate
import bcrypt


router = APIRouter(
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=UserResponse)
async def create_user(item: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = bcrypt.hashpw(item.password.encode('utf-8'), bcrypt.gensalt())
    db_user = UserDB(
        name=item.name,
        age=item.age,
        email=item.email,
        password=hashed_pw.decode('utf-8')  
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user= db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user

@router.patch('/{userid}', response_model=UserResponse)
async def edit_data(userid: int, update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == userid).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User Not Found')

    if update.name is not None:
        db_user.name = update.name
    if update.age is not None:
        db_user.age = update.age
    if update.email is not None:
        db_user.email = update.email
    if update.password is not None:
        if not bcrypt.checkpw(update.password.encode('utf-8'), db_user.password.encode('utf-8')):
            hashed_pw = bcrypt.hashpw(update.password.encode('utf-8'), bcrypt.gensalt())
            db_user.password = hashed_pw.decode('utf-8')

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"User `{db_user.name}` has been deleted"}