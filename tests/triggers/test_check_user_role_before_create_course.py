from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course
from models.enums import UserRoleEnum


def test_check_course_manager_role_raises_error(db_session):
    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title="title", manager_id=employee.id)
    db_session.add(course)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "The course can only be created by a user with the manager role!" in str(e.orig)


def test_check_course_manager_role_passes(db_session):
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title="title", manager_id=manager.id)
    db_session.add(course)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
