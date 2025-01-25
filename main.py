from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import models
from database import engine 
from api import tasks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.get('/')
async def home():
    return {
        'message': 'Welcome to Task Journal App'
    }

app.include_router(tasks.app)
