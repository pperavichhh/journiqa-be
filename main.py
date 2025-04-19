from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()
DATABASE_URL = os.getenv('USER_DATABASE')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    password = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

class User(BaseModel):
    name: str
    email : str
    age: int
    password: str

class UserCreate(User):
    pass

class UserResponse(User):
    id: int
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post("/users/", response_model=UserResponse)
async def create_item(item: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = bcrypt.hashpw(item.password.encode('utf-8'))
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

@app.get("/users/", response_model=List[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user= db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user

from typing import Optional
from pydantic import BaseModel

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

@app.patch('/users/{userid}', response_model=UserResponse)
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


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"User `{db_user.name}` has been deleted"}