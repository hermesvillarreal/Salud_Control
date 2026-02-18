from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship, AutoString
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class CalculatorType(str, Enum):
    TDEE = "tdee"
    MACRO = "macro"
    BMI = "bmi"
    ASCVD = "ascvd"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"  # 1.2
    LIGHT = "light"  # 1.375
    MODERATE = "moderate"  # 1.55
    VERY_ACTIVE = "very_active"  # 1.725
    EXTRA_ACTIVE = "extra_active"  # 1.9

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER, sa_type=AutoString)
    
    # Nutritional Goals
    daily_calories_goal: Optional[int] = None
    daily_protein_goal: Optional[int] = None
    daily_carbs_goal: Optional[int] = None
    daily_fat_goal: Optional[int] = None

class UserCreate(UserBase):
    password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    telegram_chat_id: Optional[int] = Field(default=None, index=True)
    telegram_auth_token: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Nutritional Goals (Persisted)
    daily_calories_goal: Optional[int] = None
    daily_protein_goal: Optional[int] = None
    daily_carbs_goal: Optional[int] = None
    daily_fat_goal: Optional[int] = None
    current_goal: Optional[str] = None

    # Relationships (Optional but good practice)
    weight_records: list["WeightRecord"] = Relationship(back_populates="user")
    bp_records: list["BloodPressureRecord"] = Relationship(back_populates="user")
    glucose_records: list["GlucoseRecord"] = Relationship(back_populates="user")
    food_records: list["FoodRecord"] = Relationship(back_populates="user")
    exercise_records: list["ExerciseRecord"] = Relationship(back_populates="user")
    clinical_documents: list["ClinicalDocument"] = Relationship(back_populates="user")
    calculator_results: list["CalculatorResult"] = Relationship(back_populates="user")

class WeightRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fecha_hora: datetime = Field(default_factory=datetime.now)
    weight: float
    notes: Optional[str] = None

    user: User = Relationship(back_populates="weight_records")

class BloodPressureRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fecha_hora: datetime = Field(default_factory=datetime.now)
    systolic: int
    diastolic: int
    heart_rate: Optional[int] = None
    notes: Optional[str] = None

    user: User = Relationship(back_populates="bp_records")

class GlucoseRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fecha_hora: datetime = Field(default_factory=datetime.now)
    glucose_level: float
    measurement_type: str  # e.g., ayuno, postprandial
    notes: Optional[str] = None

    user: User = Relationship(back_populates="glucose_records")

class MealType(str, Enum):
    DESAYUNO = "desayuno"
    MERIENDA_MANANA = "merienda_manana"
    ALMUERZO = "almuerzo"
    MERIENDA_TARDE = "merienda_tarde"
    CENA = "cena"
    MERIENDA_POSTCENA = "merienda_postcena"

class FoodRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fecha_hora: datetime = Field(default_factory=datetime.now)
    meal_type: MealType = Field(sa_type=AutoString)
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
    fecha_hora: datetime = Field(default_factory=datetime.now)
    exercise_type: str
    duration_minutes: int
    calories_burned: Optional[int] = None
    intensity: IntensityType = Field(sa_type=AutoString)

    user: User = Relationship(back_populates="exercise_records")

class DocumentType(str, Enum):
    RECETA = "receta"
    LABORATORIO = "laboratorio"
    ESTUDIO = "estudio"
    IMAGEN = "imagen"

class ClinicalDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    fecha_hora: datetime = Field(default_factory=datetime.now)
    title: str
    document_type: DocumentType = Field(sa_type=AutoString)
    file_path: str
    notes: Optional[str] = None

    user: User = Relationship(back_populates="clinical_documents")

class CalculatorResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    calculator_type: CalculatorType = Field(sa_type=AutoString)
    fecha_hora: datetime
    
    # Input parameters (stored as JSON for flexibility)
    input_data: str  # JSON string of inputs
    
    # Output results (stored as JSON for flexibility)
    result_data: str  # JSON string of results
    
    notes: Optional[str] = None
    
    user: User = Relationship(back_populates="calculator_results")
