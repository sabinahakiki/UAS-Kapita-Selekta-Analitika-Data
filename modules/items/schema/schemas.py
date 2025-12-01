# modules/items/schema/schemas.py
from pydantic import BaseModel
from typing import Optional

class StudentBase(BaseModel):
    student_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    department: Optional[str] = None
    attendance_percent: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    assignments_avg: Optional[float] = None
    quizzes_avg: Optional[float] = None
    participation_score: Optional[float] = None
    projects_score: Optional[float] = None
    total_score: Optional[float] = None
    grade: Optional[str] = None
    study_hours_per_week: Optional[float] = None
    extracurricular_activities: Optional[str] = None
    internet_access_at_home: Optional[str] = None
    parent_education_level: Optional[str] = None
    family_income_level: Optional[str] = None
    stress_level: Optional[int] = None
    sleep_hours_per_night: Optional[float] = None

class StudentCreate(StudentBase):
    password: Optional[str] = None

class StudentOut(StudentBase):
    id: int

    class Config:
        orm_mode = True

class PasswordUpdate(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    student_db_id: Optional[int] = None
    student_id: Optional[str] = None
    exp: Optional[int] = None
