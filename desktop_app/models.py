from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password_hash = Column(String)
    
    # Keep old relationship for migration purposes
    health_records = relationship("HealthRecord", back_populates="user")
    
    # New relationships for separated tables
    weight_records = relationship("WeightRecord", back_populates="user", cascade="all, delete-orphan")
    blood_pressure_records = relationship("BloodPressureRecord", back_populates="user", cascade="all, delete-orphan")
    glucose_records = relationship("GlucoseRecord", back_populates="user", cascade="all, delete-orphan")
    food_records = relationship("FoodRecord", back_populates="user", cascade="all, delete-orphan")
    exercise_records = relationship("ExerciseRecord", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Keep old HealthRecord for migration purposes
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

# New separate tables
class WeightRecord(Base):
    __tablename__ = "weight_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="weight_records")

class BloodPressureRecord(Base):
    __tablename__ = "blood_pressure_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="blood_pressure_records")

class GlucoseRecord(Base):
    __tablename__ = "glucose_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    glucose_level = Column(Float, nullable=False)
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="glucose_records")

class FoodRecord(Base):
    __tablename__ = "food_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    meals = Column(String)  # Stored as JSON string
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="food_records")

class ExerciseRecord(Base):
    __tablename__ = "exercise_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    exercise_type = Column(String)
    duration_minutes = Column(Integer)
    calories_burned = Column(Integer)
    intensity = Column(String)
    notes = Column(String)
    source = Column(String)
    sync_date = Column(String)
    
    user = relationship("User", back_populates="exercise_records")