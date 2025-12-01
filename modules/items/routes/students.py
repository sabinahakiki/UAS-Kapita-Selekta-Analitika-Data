# modules/items/routes/students.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_admin, get_current_user, get_password_hash
from modules.items.models import Student
from modules.items.schema.schemas import PasswordUpdate, StudentOut, StudentCreate

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

@router.get("/", response_model=List[StudentOut])
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

# 1️⃣ GET by internal numeric id (primary key)
@router.get("/id/{id}", response_model=StudentOut)
def get_student_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 2️⃣ GET by student_id like "S1000"
@router.get("/{student_id}", response_model=StudentOut)
def get_student_by_student_id(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user["role"] == "student" and student.student_id != current_user["student"].student_id:
        raise HTTPException(status_code=403, detail="Not allowed to view other students")
    return student

@router.post("/", response_model=StudentOut)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    existing = db.query(Student).filter(Student.student_id == student_in.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="student_id already exists")

    student_data = student_in.dict()
    password = student_data.pop("password", None)
    student = Student(**student_data)
    if password:
        student.hashed_password = get_password_hash(password)

    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.post("/{student_id}/password", response_model=StudentOut)
def set_student_password(
    student_id: str,
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.hashed_password = get_password_hash(payload.password)
    db.commit()
    db.refresh(student)
    return student
