from fastapi import FastAPI
import models
from database import engine 
from api import tasks

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get('/')
async def home():
    return {
        'message': 'Welcome to Task Journal App'
    }

app.include_router(tasks.app)
