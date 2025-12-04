# main.py
from fastapi import FastAPI
from database import Base, engine
from auth import router as auth_router
from modules.items.routes.students import router as students_router
from modules.items.routes.analytics import router as analytics_router
from modules.items.routes.participations import router as participations_router

# create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Learning Activity Tracker")

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(analytics_router)
app.include_router(participations_router)
