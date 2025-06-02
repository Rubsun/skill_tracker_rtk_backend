import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from db import get_db_url


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", get_db_url("config/.env.test_db"))
    command.upgrade(alembic_cfg, "head")
    # command.downgrade(alembic_cfg, "-1")
    yield


@pytest.fixture(scope="session")
def engine():
    return create_engine(get_db_url("config/.env.test_db"))


@pytest.fixture(scope="function")
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function", autouse=True)
def reset_tables(db_session):
    db_session.execute(text("TRUNCATE TABLE employee_content_statuses CASCADE"))
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
