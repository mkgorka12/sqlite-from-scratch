import pytest
from src.database import Database

@pytest.fixture
def db():
    database = Database("Chinook_Sqlite.sqlite")
    with database as active_db:
        yield active_db

def test_page_size(db):
    assert db.page_size == 1024
