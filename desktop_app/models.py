from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
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
    date = Column(Date)
    weight = Column(Float)
    blood_pressure_sys = Column(Integer)
    blood_pressure_dia = Column(Integer)
    glucose_level = Column(Float)
    notes = Column(String)
    
    user = relationship("User", back_populates="health_records")