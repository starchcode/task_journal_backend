from fastapi import FastAPI
from models import tasks
from database import engine 

app = FastAPI()
tasks.Base.metadata.create_all(bind=engine)

@app.get('/')
async def home():
    return {
        'message': 'Welcome to Task Journal App'
    }
