from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import Depends
from typing import Annotated

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
