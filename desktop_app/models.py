from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    health_records = relationship("HealthRecord", back_populates="user")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)  # Stored as TEXT in SQLite
    weight = Column(Float)
    blood_pressure_sys = Column(Integer)
    blood_pressure_dia = Column(Integer)
    glucose_level = Column(Float)
    meals = Column(String) # Stored as JSON string
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="health_records")