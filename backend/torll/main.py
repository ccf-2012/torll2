from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from torll.db.database import SessionLocal, engine, Base, get_db
from torll.models import models
from torll.api import endpoints

app = FastAPI()

origins = [
    "http://localhost:5006",
    "http://localhost",
    "http://127.0.0.1:5006",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/db_test")
def db_test(db: Session = Depends(get_db)):
    return {"message": "Database connection successful!"}

app.include_router(endpoints.router)
