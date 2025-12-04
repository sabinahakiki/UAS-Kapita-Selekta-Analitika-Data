# modules/items/routes/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from auth import get_current_admin
from database import get_db
from modules.items.models import Student

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)

def _to_float(v):
    return float(v) if v is not None else None

@router.get("/study-duration")
def study_duration(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    overall = (
        db.query(func.avg(Student.study_hours_per_week))
        .filter(Student.study_hours_per_week.isnot(None))
        .scalar()
    )

    by_department = (
        db.query(
            Student.department,
            func.avg(Student.study_hours_per_week),
            func.count(Student.id),
        )
        .filter(Student.department.isnot(None), Student.study_hours_per_week.isnot(None))
        .group_by(Student.department)
        .all()
    )

    return {
        "overall_avg_hours_per_week": _to_float(overall),
        "by_department": [
            {
                "department": dept,
                "avg_hours_per_week": _to_float(avg),
                "student_count": count,
            }
            for dept, avg, count in by_department
        ],
    }

@router.get("/study-duration/{department}")
def study_duration_by_department(
    department: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    students = (
        db.query(Student)
        .filter(
            Student.department == department,
            Student.study_hours_per_week.isnot(None),
        )
        .all()
    )

    if not students:
        raise HTTPException(status_code=404, detail="No students found for this department")

    avg_hours = (
        db.query(func.avg(Student.study_hours_per_week))
        .filter(
            Student.department == department,
            Student.study_hours_per_week.isnot(None),
        )
        .scalar()
    )
    avg_attendance = (
        db.query(func.avg(Student.attendance_percent))
        .filter(
            Student.department == department,
            Student.attendance_percent.isnot(None),
        )
        .scalar()
    )
    avg_midterm = (
        db.query(func.avg(Student.midterm_score))
        .filter(
            Student.department == department,
            Student.midterm_score.isnot(None),
        )
        .scalar()
    )
    avg_final = (
        db.query(func.avg(Student.final_score))
        .filter(
            Student.department == department,
            Student.final_score.isnot(None),
        )
        .scalar()
    )
    avg_stress = (
        db.query(func.avg(Student.stress_level))
        .filter(
            Student.department == department,
            Student.stress_level.isnot(None),
        )
        .scalar()
    )
    avg_sleep = (
        db.query(func.avg(Student.sleep_hours_per_night))
        .filter(
            Student.department == department,
            Student.sleep_hours_per_night.isnot(None),
        )
        .scalar()
    )

    return {
        "department": department,
        "avg_hours_per_week": _to_float(avg_hours),
        "student_count": len(students),
        "related_metrics": {
            "avg_attendance_percent": _to_float(avg_attendance),
            "avg_midterm_score": _to_float(avg_midterm),
            "avg_final_score": _to_float(avg_final),
            "avg_stress_level": _to_float(avg_stress),
            "avg_sleep_hours_per_night": _to_float(avg_sleep),
        },
        "students": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "name": " ".join(filter(None, [s.first_name, s.last_name])),
                "study_hours_per_week": _to_float(s.study_hours_per_week),
                "attendance_percent": _to_float(s.attendance_percent),
                "midterm_score": _to_float(s.midterm_score),
                "final_score": _to_float(s.final_score),
                "grade": s.grade,
                "stress_level": _to_float(s.stress_level),
                "sleep_hours_per_night": _to_float(s.sleep_hours_per_night),
            }
            for s in students
        ],
    }

@router.get("/study-duration/{department}/{student_name}")
def study_duration_by_department_and_student(
    department: str,
    student_name: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    # simple case-insensitive match on first/last/full name
    name_like = f"%{student_name}%"
    matches = (
        db.query(Student)
        .filter(
            Student.department == department,
            Student.study_hours_per_week.isnot(None),
            or_(
                Student.first_name.ilike(name_like),
                Student.last_name.ilike(name_like),
                func.concat(Student.first_name, " ", Student.last_name).ilike(name_like),
            ),
        )
        .all()
    )

    if not matches:
        raise HTTPException(status_code=404, detail="No matching students found in this department")

    avg_hours = sum([s.study_hours_per_week for s in matches if s.study_hours_per_week is not None]) / len(matches)

    return {
        "department": department,
        "query": student_name,
        "avg_hours_per_week": _to_float(avg_hours),
        "student_count": len(matches),
        "students": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "name": " ".join(filter(None, [s.first_name, s.last_name])),
                "study_hours_per_week": _to_float(s.study_hours_per_week),
                "attendance_percent": _to_float(s.attendance_percent),
                "midterm_score": _to_float(s.midterm_score),
                "final_score": _to_float(s.final_score),
                "grade": s.grade,
                "stress_level": _to_float(s.stress_level),
                "sleep_hours_per_night": _to_float(s.sleep_hours_per_night),
            }
            for s in matches
        ],
    }
