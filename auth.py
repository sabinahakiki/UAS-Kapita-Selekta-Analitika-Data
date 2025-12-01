# auth.py
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from modules.items.models import Student
from modules.items.schema.schemas import Token

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

pwd_context = CryptContext(
    # pbkdf2_sha256 avoids bcrypt's 72-byte limit; bcrypt variants kept for backward compatibility if any
    schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/auth", tags=["auth"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # pbkdf2_sha256 handles long inputs without truncation
    return pwd_context.hash(password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_admin(username: str, password: str) -> Optional[Dict]:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"username": username, "role": "admin"}
    return None

def authenticate_student(username: str, password: str, db: Session) -> Optional[Dict]:
    student = db.query(Student).filter(Student.student_id == username).first()
    if not student or not student.hashed_password:
        return None
    if not verify_password(password, student.hashed_password):
        return None
    return {
        "username": username,
        "role": "student",
        "student_db_id": student.id,
        "student_id": student.student_id,
    }

def authenticate_user(username: str, password: str, db: Session) -> Optional[Dict]:
    admin_user = authenticate_admin(username, password)
    if admin_user:
        return admin_user
    return authenticate_student(username, password, db)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        student_db_id = payload.get("student_db_id")
        if username is None or role is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    if role == "admin":
        return {"username": username, "role": "admin"}

    if role == "student":
        student = db.query(Student).filter(Student.id == student_db_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return {"username": username, "role": "student", "student": student}

    raise credentials_exception

def get_current_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def get_current_student(current_user: Dict = Depends(get_current_user)) -> Student:
    if current_user.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student privileges required")
    return current_user["student"]

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    access_token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"],
            "student_db_id": user.get("student_db_id"),
            "student_id": user.get("student_id"),
        }
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@router.get("/me")
def read_me(current_user: Dict = Depends(get_current_user)):
    payload = {"username": current_user["username"], "role": current_user["role"]}
    if current_user["role"] == "student":
        payload["student_id"] = current_user["student"].student_id
    return payload
