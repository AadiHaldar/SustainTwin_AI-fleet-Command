from sqlalchemy import Column, String, Integer, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Operator") # Admin, Operator, Engineer
    is_active = Column(Boolean, default=True)
