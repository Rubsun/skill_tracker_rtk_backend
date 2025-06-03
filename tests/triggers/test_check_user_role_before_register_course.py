from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, CourseEmployee
from models.enums import UserRoleEnum


def test_check_course_employee_role_raises_error(db_session):
    """
    Test that associating a CourseEmployee with a user who does not have the employee role raises a DBAPIError.
    Ensures only users with the employee role can be registered for courses.
    """
    not_employee = User(given_name='not_employee', family_name='not_employee', username='not_employee', password_hash='hash')
    db_session.add(not_employee)
    db_session.flush()

    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title="title", manager_id=manager.id)
    db_session.add(course)
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=not_employee.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "Only a user with the employee role can register for the courses!" in str(e.orig)


def test_check_course_employee_role_passes(db_session):
    """
    Test that associating a CourseEmployee with a valid employee user commits successfully.
    Validates role-based restrictions on course enrollment.
    """
    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.flush()

    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title="title", manager_id=manager.id)
    db_session.add(course)
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
