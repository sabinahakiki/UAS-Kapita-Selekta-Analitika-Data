# modules/items/routes/participations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_current_admin, get_current_student
from database import get_db
from modules.items.models import Student

router = APIRouter(
    prefix="/participations",
    tags=["participations"],
)

# Map the 0-100 participation_score to a 0-6 scale for easier categorization.
GOOD_MIN_0_6 = 4.5   # good: >= 4.5 (≈75/100)
AVERAGE_MIN_0_6 = 2  # average: >= 2.0 and < 4.5 (≈33.3/100 to <75/100)

GOOD_MIN_PERCENT = (GOOD_MIN_0_6 / 6) * 100
AVERAGE_MIN_PERCENT = (AVERAGE_MIN_0_6 / 6) * 100


def _to_float(v):
    return float(v) if v is not None else None


def _score_to_scale_0_6(score_0_100):
    """Convert 0-100 participation_score to a 0-6 scale."""
    if score_0_100 is None:
        return None
    return round((score_0_100 / 100) * 6, 2)


def _student_payload(student: Student):
    return {
        "id": student.id,
        "student_id": student.student_id,
        "name": " ".join(filter(None, [student.first_name, student.last_name])),
        "participation_score": _to_float(student.participation_score),
        "participation_level_0_6": _score_to_scale_0_6(student.participation_score),
    }


@router.get("/")
def list_participations(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    students = (
        db.query(Student)
        .filter(Student.participation_score.isnot(None))
        .order_by(Student.participation_score.desc())
        .all()
    )

    avg_score = (
        db.query(func.avg(Student.participation_score))
        .filter(Student.participation_score.isnot(None))
        .scalar()
    )

    return {
        "count": len(students),
        "average_participation_score": _to_float(avg_score),
        "average_participation_level_0_6": _score_to_scale_0_6(avg_score),
        "students": [_student_payload(s) for s in students],
    }


def _category_response(
    db: Session,
    filters,
    category_label: str,
):
    students = (
        db.query(Student)
        .filter(Student.participation_score.isnot(None), *filters)
        .order_by(Student.participation_score.desc())
        .all()
    )
    return {
        "category": category_label,
        "count": len(students),
        "thresholds_0_6": {
            "good_min": GOOD_MIN_0_6,
            "average_min": AVERAGE_MIN_0_6,
        },
        "students": [_student_payload(s) for s in students],
    }


@router.get("/good")
def participations_good(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [Student.participation_score >= GOOD_MIN_PERCENT]
    return _category_response(db, filters, "good (>=4.5 on 0-6 scale)")


@router.get("/average")
def participations_average(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [
        Student.participation_score >= AVERAGE_MIN_PERCENT,
        Student.participation_score < GOOD_MIN_PERCENT,
    ]
    return _category_response(db, filters, "average (2.0-4.49 on 0-6 scale)")


@router.get("/bad")
def participations_bad(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [Student.participation_score < AVERAGE_MIN_PERCENT]
    return _category_response(db, filters, "bad (<2.0 on 0-6 scale)")

@router.get("/me")
def participations_me(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    student = db.query(Student).filter(Student.id == current_student.id).first()
    if not student or student.participation_score is None:
        return {
            "student_id": current_student.student_id,
            "name": _student_payload(current_student)["name"],
            "participation_score": None,
            "participation_level_0_6": None,
            "note": "No participation score recorded.",
        }

    return _student_payload(student)
