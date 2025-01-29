from sqlalchemy import Boolean, Column, Integer, String, Text, Date
from sqlalchemy.sql import func
from database import Base
from pgvector.sqlalchemy import Vector

class Tasks(Base):
    __tablename__ = 'task_journal'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text) 
    deadline = Column(Date, default=func.current_date())
    is_completed = Column(Boolean, default=False)
    title_embedding = Column(Vector(1536)) 
    description_embedding = Column(Vector(1536)) 
