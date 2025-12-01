# import_students.py
import pandas as pd
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from modules.items.models import Student

Base.metadata.create_all(bind=engine)

CSV_PATH = "data/students_kaggle.csv"

def to_int(v):
    if pd.isna(v):
        return None
    return int(v)

def to_float(v):
    if pd.isna(v):
        return None
    return float(v)

def to_str(v):
    if pd.isna(v):
        return None
    return str(v)

def import_students():
    df = pd.read_csv(CSV_PATH)

    df = df.rename(columns={
        "Student_ID": "student_id",
        "First_Name": "first_name",
        "Last_Name": "last_name",
        "Email": "email",
        "Gender": "gender",
        "Age": "age",
        "Department": "department",
        "Attendance (%)": "attendance_percent",
        "Midterm_Score": "midterm_score",
        "Final_Score": "final_score",
        "Assignments_Avg": "assignments_avg",
        "Quizzes_Avg": "quizzes_avg",
        "Participation_Score": "participation_score",
        "Projects_Score": "projects_score",
        "Total_Score": "total_score",
        "Grade": "grade",
        "Study_Hours_per_Week": "study_hours_per_week",
        "Extracurricular_Activities": "extracurricular_activities",
        "Internet_Access_at_Home": "internet_access_at_home",
        "Parent_Education_Level": "parent_education_level",
        "Family_Income_Level": "family_income_level",
        "Stress_Level (1-10)": "stress_level",
        "Sleep_Hours_per_Night": "sleep_hours_per_night",
    })

    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            student = Student(
                student_id=to_str(row.get("student_id")),
                first_name=to_str(row.get("first_name")),
                last_name=to_str(row.get("last_name")),
                email=to_str(row.get("email")),
                gender=to_str(row.get("gender")),
                age=to_int(row.get("age")),
                department=to_str(row.get("department")),
                attendance_percent=to_float(row.get("attendance_percent")),
                midterm_score=to_float(row.get("midterm_score")),
                final_score=to_float(row.get("final_score")),
                assignments_avg=to_float(row.get("assignments_avg")),
                quizzes_avg=to_float(row.get("quizzes_avg")),
                participation_score=to_float(row.get("participation_score")),
                projects_score=to_float(row.get("projects_score")),
                total_score=to_float(row.get("total_score")),
                grade=to_str(row.get("grade")),
                study_hours_per_week=to_float(row.get("study_hours_per_week")),
                extracurricular_activities=to_str(row.get("extracurricular_activities")),
                internet_access_at_home=to_str(row.get("internet_access_at_home")),
                parent_education_level=to_str(row.get("parent_education_level")),
                family_income_level=to_str(row.get("family_income_level")),
                stress_level=to_int(row.get("stress_level")),
                sleep_hours_per_night=to_float(row.get("sleep_hours_per_night")),
            )
            db.add(student)

        db.commit()
        print("✅ Import selesai")
    except Exception as e:
        db.rollback()
        print("❌ Error saat import:", e)
    finally:
        db.close()

if __name__ == "__main__":
    import_students()
