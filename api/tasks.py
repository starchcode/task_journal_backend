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
