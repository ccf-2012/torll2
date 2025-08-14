from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from torll.db.database import SessionLocal, engine, Base
from torll.models import models
from torll.api import endpoints

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/db_test")
def db_test(db: Session = Depends(get_db)):
    return {"message": "Database connection successful!"}

app.include_router(endpoints.router)
