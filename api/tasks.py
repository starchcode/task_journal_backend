from fastapi import APIRouter, HTTPException
import models
import schemas
import dependencies

app = APIRouter()

db = dependencies.db_dependency

@app.get('/tasks')
async def get_tasks(db:db):
    result = db.query(models.Tasks).all()

    return result


@app.post("/tasks")
async def create_questions(task: schemas.TaskBase, db:db):
    new_task = models.Tasks(title=task.title,
                               description= task.description,
                               deadline=task.deadline,
                               )

    try:
        # Add to session and commit
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")  # Include exception message
    
    return new_task

@app.patch("/tasks/{task_id}")
async def update_task(task_id: int, is_completed: bool, db: db):
    task = db.query(models.Tasks).filter(models.Tasks.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = is_completed

    try:
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

    return task

