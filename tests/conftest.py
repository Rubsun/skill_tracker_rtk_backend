import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from db import get_db_url


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    Automatically apply all Alembic migrations to the test database at the start of the test session.
    Ensures the test database schema is up-to-date before any tests run.
    """
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", get_db_url("config/.env.test_db"))
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture(scope="session")
def engine():
    """
    Create and return a SQLAlchemy engine connected to the test database.
    This fixture has session scope and is reused across all tests.
    """
    return create_engine(get_db_url("config/.env.test_db"))


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Provide a new SQLAlchemy session for each test function.
    The session is created before the test and closed after the test completes.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function", autouse=True)
def reset_tables(db_session):
    """
    Truncate all relevant tables in the test database before each test function.
    This ensures a clean state for tests by removing all existing data.
    """
    db_session.execute(text("TRUNCATE TABLE course_employee_contents CASCADE"))
    db_session.execute(text("TRUNCATE TABLE comments CASCADE"))
    db_session.execute(text("TRUNCATE TABLE course_employees CASCADE"))
    db_session.execute(text("TRUNCATE TABLE contents CASCADE"))
    db_session.execute(text("TRUNCATE TABLE courses CASCADE"))
    db_session.execute(text("TRUNCATE TABLE tasks CASCADE"))
    db_session.execute(text("TRUNCATE TABLE theories CASCADE"))
    db_session.execute(text("TRUNCATE TABLE user_roles CASCADE"))
    db_session.execute(text("TRUNCATE TABLE users CASCADE"))
    db_session.commit()
    yield
