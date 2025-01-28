import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app  
import models
from dependencies import get_db  
from datetime import date

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    models.Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)  # Drop tables after tests

@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db  # Override db
    return TestClient(app)



def test_read_tasks(client, test_db):
    # Given: Create a task in the database
    today_date = date.today()
    task1 = models.Tasks(title='task 1', description='task 1 desc', deadline=today_date)
    test_db.add(task1)
    test_db.commit()
    test_db.refresh(task1)

    response = client.get("/tasks/")

    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 1
    
    task = tasks[0]
    assert task['title'] == 'task 1'
    assert task['description'] == 'task 1 desc'
    assert task['deadline'] == today_date.strftime('%Y-%m-%d')

    # Optional: Verify that the task ID exists
    assert 'id' in task


def test_create_task(client, test_db):
    # Given: Valid task data
    task_data = {
        "title": "Test Task",
        "description": "This is a test task.",
        "deadline": date.today().strftime('%Y-%m-%d')  
    }

    response = client.post("/tasks", json=task_data)

    assert response.status_code == 200
    task = response.json()

    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]
    assert task["deadline"] == task_data["deadline"]
    assert "id" in task

    db_task = test_db.query(models.Tasks).filter(models.Tasks.id == task["id"]).first()
    assert db_task is not None
    assert db_task.title == task_data["title"]
    assert db_task.description == task_data["description"]
    assert db_task.deadline.strftime('%Y-%m-%d') == task_data["deadline"]

def test_create_task_with_invalid_data(client):
    task_data = {
        "description": "Missing title",
        "deadline": date.today().strftime('%Y-%m-%d')
    }

    response = client.post("/tasks", json=task_data)

    assert response.status_code == 422
    assert "detail" in response.json()
