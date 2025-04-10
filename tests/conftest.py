import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.db import Base
from tests.support.app_driver import AppDriver

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope='session')
def app():
    app = AppDriver()
    try:
        app.start()
        yield app
    finally:
        app.stop()


TEST_DATABASE_URL = "sqlite:///./test_service.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fixture to provide a clean database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    yield session  # Provide the session to the test

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Remove the database file
    if os.path.exists("test_service.db"):
        os.remove("test_service.db")
