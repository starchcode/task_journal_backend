import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app  # Import your FastAPI app
import models
from dependencies import get_db  # Import original get_db function
from datetime import date

# Create a separate in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db to use the test database
@pytest.fixture
def test_db():
    models.Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)  # Drop tables after tests

# Override FastAPI dependency
@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db  # Override db
    return TestClient(app)


def test_read_tasks(client, test_db):
    today_date = date.today()
    task1 = models.Tasks(title='task 1', description= 'task 1 desc', deadline=today_date)
    test_db.add(task1)
    test_db.commit()
    test_db.refresh(task1)

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'task 1'
    assert response.json()[0]['description'] == 'task 1 desc'
    assert response.json()[0]['deadline'] == today_date.strftime('%Y-%m-%d')

