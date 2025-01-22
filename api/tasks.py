from fastapi import APIRouter
import models
import schemas
import dependencies

app = APIRouter()

db = dependencies.db_dependency

@app.post("/tasks")
async def create_questions(task: schemas.TaskBase, db:db):
    new_task = models.Tasks(title=task.title,
                               description= task.description,
                               deadline=task.deadline,
                               )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
