from pydantic import BaseModel, Field, field_validator
from typing import Optional
import html
from datetime import date

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    deadline: Optional[date] = None 
    is_completed: Optional[bool] = None 

    def __init__(self, **data):
        super().__init__(**data)
        if self.description:
            self.description = html.escape(self.description)  # Sanitization

    @field_validator('deadline')
    def check_deadline(cls, v):
        if v and v < date.today():
            raise ValueError('Deadline cannot be in the past')
        return v


class TaskUpdate(BaseModel):
    is_completed: bool
