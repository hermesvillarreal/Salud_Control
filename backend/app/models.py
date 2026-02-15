from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)

class UserCreate(UserBase):
    password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    telegram_chat_id: Optional[int] = Field(default=None, index=True)
    telegram_auth_token: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (Optional but good practice)
    weight_records: list["WeightRecord"] = Relationship(back_populates="user")
    bp_records: list["BloodPressureRecord"] = Relationship(back_populates="user")
    glucose_records: list["GlucoseRecord"] = Relationship(back_populates="user")
    food_records: list["FoodRecord"] = Relationship(back_populates="user")
    exercise_records: list["ExerciseRecord"] = Relationship(back_populates="user")
    clinical_documents: list["ClinicalDocument"] = Relationship(back_populates="user")

class WeightRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    weight: float
    notes: Optional[str] = None

    user: User = Relationship(back_populates="weight_records")

class BloodPressureRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    systolic: int
    diastolic: int
    heart_rate: Optional[int] = None
    notes: Optional[str] = None

    user: User = Relationship(back_populates="bp_records")

class GlucoseRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    glucose_level: float
    measurement_type: str  # e.g., ayuno, postprandial
    notes: Optional[str] = None

    user: User = Relationship(back_populates="glucose_records")

class MealType(str, Enum):
    DESAYUNO = "desayuno"
    ALMUERZO = "almuerzo"
    CENA = "cena"
    SNACK = "snack"

class FoodRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    meal_type: MealType
    description: str
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    image_url: Optional[str] = None

    user: User = Relationship(back_populates="food_records")

class IntensityType(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class ExerciseRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    exercise_type: str
    duration_minutes: int
    calories_burned: Optional[int] = None
    intensity: IntensityType

    user: User = Relationship(back_populates="exercise_records")

class DocumentType(str, Enum):
    RECETA = "receta"
    LABORATORIO = "laboratorio"
    ESTUDIO = "estudio"
    IMAGEN = "imagen"

class ClinicalDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    document_type: DocumentType
    file_path: str
    notes: Optional[str] = None

    user: User = Relationship(back_populates="clinical_documents")
