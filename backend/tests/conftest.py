import pytest
import os
import shutil

# MUST SET ENV VAR BEFORE IMPORTING DATABASE
TEST_DATABASE_URL = "sqlite:///./test_embroidery.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db, init_db
from backend.main import app

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Ensure a clean slate
    if os.path.exists("./test_embroidery.db"):
        os.remove("./test_embroidery.db")
    
    Base.metadata.create_all(bind=engine)
    init_db(session=TestingSessionLocal()) # Seed necessary system state rows
    yield
    # Cleanup after all tests
    if os.path.exists("./test_embroidery.db"):
        os.remove("./test_embroidery.db")

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def temp_library(tmp_path):
    lib_dir = tmp_path / "library"
    lib_dir.mkdir()
    return lib_dir

@pytest.fixture
def temp_inbox(tmp_path):
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    return inbox_dir
