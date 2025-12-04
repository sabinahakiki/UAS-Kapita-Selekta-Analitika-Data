# modules/items/routes/analytics.py
import math

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

def _mean(values):
    return sum(values) / len(values) if values else None

def _pearson(xs, ys):
    if len(xs) < 2 or len(ys) < 2 or len(xs) != len(ys):
        return None
    mx, my = _mean(xs), _mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)

def _percentile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    k = (len(ordered) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return ordered[int(k)]
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)

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

def _name(student: Student):
    return " ".join(filter(None, [student.first_name, student.last_name]))

def _to_binary_yes_no(value):
    if value is None:
        return None
    v = str(value).strip().lower()
    if v == "yes":
        return 1
    if v == "no":
        return 0
    return None

@router.get("/activity-correlation/final-score")
def activity_correlation_final_score(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    records = db.query(
        Student.quizzes_avg,
        Student.study_hours_per_week,
        Student.extracurricular_activities,
        Student.attendance_percent,
        Student.sleep_hours_per_night,
        Student.final_score,
    ).all()

    def collect(metric_getter):
        pairs = []
        for rec in records:
            x = metric_getter(rec)
            y = rec.final_score
            if x is None or y is None:
                continue
            pairs.append((float(x), float(y)))
        return pairs

    metrics = [
        ("quizzes_avg", lambda r: r.quizzes_avg, "Average quiz score"),
        ("study_hours_per_week", lambda r: r.study_hours_per_week, "Study hours per week"),
        ("extracurricular_activities", lambda r: _to_binary_yes_no(r.extracurricular_activities), "Extracurricular (Yes=1, No=0)"),
        ("attendance_percent", lambda r: r.attendance_percent, "Attendance percent"),
        ("sleep_hours_per_night", lambda r: r.sleep_hours_per_night, "Sleep hours per night"),
    ]

    payload = []
    for key, getter, label in metrics:
        pairs = collect(getter)
        if not pairs:
            payload.append({"metric": key, "description": label, "count": 0, "pearson_r": None, "mean_metric": None, "mean_final_score": None})
            continue
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        payload.append({
            "metric": key,
            "description": label,
            "count": len(pairs),
            "pearson_r": _to_float(_pearson(xs, ys)),
            "mean_metric": _to_float(_mean(xs)),
            "mean_final_score": _to_float(_mean(ys)),
        })

    return {
        "target": "final_score",
        "metrics": payload,
        "note": "Pearson correlation; extracurricular_activities converted to Yes=1, No=0.",
    }

@router.get("/low-activity")
def low_activity_students(
    min_low_metrics: int = 2,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    students = db.query(Student).all()

    attendance_vals = [s.attendance_percent for s in students if s.attendance_percent is not None]
    study_vals = [s.study_hours_per_week for s in students if s.study_hours_per_week is not None]
    quiz_vals = [s.quizzes_avg for s in students if s.quizzes_avg is not None]
    sleep_vals = [s.sleep_hours_per_night for s in students if s.sleep_hours_per_night is not None]

    thresholds = {
        "attendance_percent": _to_float(_percentile(attendance_vals, 0.25)),
        "study_hours_per_week": _to_float(_percentile(study_vals, 0.25)),
        "quizzes_avg": _to_float(_percentile(quiz_vals, 0.25)),
        "sleep_hours_per_night": _to_float(_percentile(sleep_vals, 0.25)),
    }

    low_students = []
    for s in students:
        metrics = {
            "attendance_percent": _to_float(s.attendance_percent),
            "study_hours_per_week": _to_float(s.study_hours_per_week),
            "quizzes_avg": _to_float(s.quizzes_avg),
            "sleep_hours_per_night": _to_float(s.sleep_hours_per_night),
        }
        low_flags = [
            key for key, value in metrics.items()
            if value is not None and thresholds[key] is not None and value <= thresholds[key]
        ]
        if len(low_flags) >= min_low_metrics:
            low_students.append({
                "id": s.id,
                "student_id": s.student_id,
                "name": _name(s),
                "low_metric_count": len(low_flags),
                "low_metrics": low_flags,
                "metrics": metrics,
            })

    low_students.sort(key=lambda x: x["low_metric_count"], reverse=True)

    return {
        "thresholds_25th_percentile": thresholds,
        "min_low_metrics": min_low_metrics,
        "low_students": low_students,
        "total_flagged": len(low_students),
    }
