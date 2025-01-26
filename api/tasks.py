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
async def update_task(task_id: int, request: schemas.TaskUpdate, db: db):
    task = db.get(models.Tasks, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    setattr(task, "is_completed", request.is_completed)

    try:
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

    return task

@app.delete("/tasks/{task_id}")
async def destroy_task(task_id: int, db: db):
    # Find the task using `get()`, which is optimized for querying by primary key
    task = db.get(models.Tasks, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db.delete(task)  # Delete the task
        db.commit()  # Commit the transaction to apply the change
    except Exception as e:
        db.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")

    return {"detail": "Task deleted successfully"}
