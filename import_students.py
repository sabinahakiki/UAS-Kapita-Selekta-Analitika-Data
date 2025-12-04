# import_students.py
import os
import pandas as pd
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from modules.items.models import Student

Base.metadata.create_all(bind=engine)

CSV_PATH = "data/students_kaggle.csv"
USE_FAKE_NAMES = os.getenv("USE_FAKE_NAMES", "1") == "1"

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

# 50 x 100 = 5000 unique name combinations to cover the full dataset deterministically
FIRST_NAMES = [
    "Liam","Noah","Oliver","Elijah","James","William","Benjamin","Lucas","Henry","Alexander",
    "Mason","Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo",
    "Jack","Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew",
    "Luke","Asher","Carter","Julian","Grayson","Leo","Jayden","Gabriel","Isaac","Lincoln",
    "Anthony","Hudson","Dylan","Ezra","Thomas","Charles","Christopher","Jaxon","Maverick","Josiah",
]
LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
]

def generate_fake_identity(student_id: str):
    """
    Deterministically generate a unique first/last/email per student_id
    so names do not repeat between records while staying reproducible.
    """
    # Extract numeric part; fallback to hash-like mod if missing digits
    digits = "".join(ch for ch in str(student_id) if ch.isdigit())
    idx = int(digits) if digits else abs(hash(student_id))

    # Map index into the name grid
    first = FIRST_NAMES[idx % len(FIRST_NAMES)]
    last = LAST_NAMES[(idx // len(FIRST_NAMES)) % len(LAST_NAMES)]

    # Tie email to student_id to avoid collisions if names wrap
    email = f"{first.lower()}.{last.lower()}_{str(student_id).lower()}@example.edu"
    return first, last, email

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
            student_id = to_str(row.get("student_id"))

            if USE_FAKE_NAMES:
                fake_first, fake_last, fake_email = generate_fake_identity(student_id)
                first_name = fake_first
                last_name = fake_last
                email = fake_email
            else:
                first_name = to_str(row.get("first_name"))
                last_name = to_str(row.get("last_name"))
                email = to_str(row.get("email"))

            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
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
