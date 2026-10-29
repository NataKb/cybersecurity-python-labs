from contextlib import asynccontextmanager
from fastapi import FastAPI

# Імпортуємо конкретні змінні з вашого shared/student.py
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

from labs.lab03.config import DOMAIN_DESCRIPTION, THRESHOLD, UNIT
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=f"Lab 03 - Variant {VARIANT_NUMBER}",
    description=f"{DOMAIN_DESCRIPTION}. Поріг: {THRESHOLD} {UNIT}.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["Service"])
def ping():
    return {"status": "ok"}


@app.get("/student", tags=["Service"])
def get_student():
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }
