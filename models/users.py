from sqlalchemy import Column, Integer, String, Float, Text
from database.users import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    password = Column(String, nullable=False)