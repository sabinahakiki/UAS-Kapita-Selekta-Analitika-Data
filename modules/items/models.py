# modules/items/models.py
from sqlalchemy import Column, Integer, String, Float
from database import Base  # database.py di root

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)

    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    department = Column(String(100), nullable=True)

    attendance_percent = Column(Float, nullable=True)
    midterm_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    assignments_avg = Column(Float, nullable=True)
    quizzes_avg = Column(Float, nullable=True)
    participation_score = Column(Float, nullable=True)
    projects_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    grade = Column(String(2), nullable=True)

    study_hours_per_week = Column(Float, nullable=True)
    extracurricular_activities = Column(String(10), nullable=True)
    internet_access_at_home = Column(String(10), nullable=True)
    parent_education_level = Column(String(50), nullable=True)
    family_income_level = Column(String(20), nullable=True)
    stress_level = Column(Integer, nullable=True)
    sleep_hours_per_night = Column(Float, nullable=True)
