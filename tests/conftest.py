import pytest
from dotenv import load_dotenv

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
