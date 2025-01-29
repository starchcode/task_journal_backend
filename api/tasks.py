from fastapi import APIRouter, HTTPException
import models
import schemas
import dependencies
from openai import OpenAI
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from typing import Optional

client = OpenAI()
app = APIRouter()
db = dependencies.db_dependency

# Helper function to generate embeddings using OpenAI
async def generate_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )

    return response.data[0].embedding

@app.get('/tasks')
async def get_tasks(db: db):
    tasks = db.query(
        models.Tasks.id,
        models.Tasks.title,
        models.Tasks.description,
        models.Tasks.deadline,
        models.Tasks.is_completed
    ).order_by(models.Tasks.deadline.asc(), models.Tasks.id.asc()).all()

    # Convert to a list of dictionaries
    result = [dict(task._mapping) for task in tasks]  

    return jsonable_encoder(result)  # Ensure JSON serializability

@app.get("/tasks/search")
async def search_tasks(db: db, query: str, search_by: str = "title", is_completed: Optional[bool] = None):
    query_embedding_1 = await generate_embedding(query)
    query_embedding = '[' + ','.join(map(str, query_embedding_1)) + ']'

    if search_by == "title":
        query_stmt = db.query(
            models.Tasks,
            func.cosine_distance(models.Tasks.title_embedding, query_embedding).label("similarity")
        )
    elif search_by == "description":
        query_stmt = db.query(
            models.Tasks,
            func.cosine_distance(models.Tasks.description_embedding, query_embedding).label("similarity")
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid search_by value. Use 'title' or 'description'.")

    if is_completed is not None:
        query_stmt = query_stmt.filter(models.Tasks.is_completed == is_completed)

    results = query_stmt.all()

    tasks = []
    for row in results:
        task = row[0] 
        similarity = row[1] 

        tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "deadline": task.deadline,
            "is_completed": task.is_completed,
            "similarity": similarity
        })

    tasks = sorted(tasks, key=lambda x: x["similarity"])

    return jsonable_encoder(tasks)


@app.post("/tasks")
async def create_questions(task: schemas.TaskBase, db:db):
    title_embedding = await generate_embedding(task.title)

    description_text = task.description if task.description else ""
    description_embedding = await generate_embedding(description_text)


    new_task = models.Tasks(title=task.title,
                            description= task.description,
                            deadline=task.deadline,
                            title_embedding=title_embedding,
                            description_embedding=description_embedding
                            )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")  # Include exception message
    
    task_dict = {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "deadline": new_task.deadline,
        "is_completed": new_task.is_completed
        }

    return jsonable_encoder(task_dict)


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
        
    task_dict = {
        "id":task.id,
        "title":task.title,
        "description":task.description,
        "deadline":task.deadline,
        "is_completed":task.is_completed
        }

    return jsonable_encoder(task_dict)

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
