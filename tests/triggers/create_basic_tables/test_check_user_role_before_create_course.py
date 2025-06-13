from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course
from models.enums import UserRoleEnum


def test_check_course_manager_role_raises_error(db_session):
    """
    Test that creating a Course with a manager_id referencing a user without the manager role raises a DBAPIError.
    Ensures only users with the manager role can create courses.
    """
    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
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
    """
    Test that creating a Course with a valid manager (user with manager role) commits successfully.
    Validates role-based access control on course creation.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
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
