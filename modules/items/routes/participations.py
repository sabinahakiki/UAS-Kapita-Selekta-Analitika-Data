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

# Participation is stored as 0-100; categorize directly on that scale.
VERY_GOOD_MIN_PERCENT = 90  # very good: >= 90%
GOOD_MIN_PERCENT = 75       # good: >= 75% and < 90%
AVERAGE_MIN_PERCENT = 50    # average: >= 50% and < 75%


def _to_float(v):
    return float(v) if v is not None else None


def _score_to_category(score_0_100):
    """Bucket participation_score into a human-readable category."""
    if score_0_100 is None:
        return None
    if score_0_100 >= VERY_GOOD_MIN_PERCENT:
        return "very-good"
    if score_0_100 >= GOOD_MIN_PERCENT:
        return "good"
    if score_0_100 >= AVERAGE_MIN_PERCENT:
        return "average"
    return "bad"


def _student_payload(student: Student):
    return {
        "id": student.id,
        "student_id": student.student_id,
        "name": " ".join(filter(None, [student.first_name, student.last_name])),
        "participation_score": _to_float(student.participation_score),
        "participation_category": _score_to_category(student.participation_score),
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
        "category_thresholds_percent": {
            "very_good_min": VERY_GOOD_MIN_PERCENT,
            "good_min": GOOD_MIN_PERCENT,
            "average_min": AVERAGE_MIN_PERCENT,
        },
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
        "thresholds_percent": {
            "very_good_min": VERY_GOOD_MIN_PERCENT,
            "good_min": GOOD_MIN_PERCENT,
            "average_min": AVERAGE_MIN_PERCENT,
        },
        "students": [_student_payload(s) for s in students],
    }


@router.get("/very-good")
def participations_very_good(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [Student.participation_score >= VERY_GOOD_MIN_PERCENT]
    return _category_response(db, filters, "very-good (>=90%)")


@router.get("/good")
def participations_good(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [
        Student.participation_score >= GOOD_MIN_PERCENT,
        Student.participation_score < VERY_GOOD_MIN_PERCENT,
    ]
    return _category_response(db, filters, "good (75-89%)")


@router.get("/average")
def participations_average(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [
        Student.participation_score >= AVERAGE_MIN_PERCENT,
        Student.participation_score < GOOD_MIN_PERCENT,
    ]
    return _category_response(db, filters, "average (50-74%)")


@router.get("/bad")
def participations_bad(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    filters = [Student.participation_score < AVERAGE_MIN_PERCENT]
    return _category_response(db, filters, "bad (<50%)")


# login sebagai student buat ngeliat data participations nya dia.
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
            "participation_category": None,
            "note": "No participation score recorded.",
        }

    return _student_payload(student)
