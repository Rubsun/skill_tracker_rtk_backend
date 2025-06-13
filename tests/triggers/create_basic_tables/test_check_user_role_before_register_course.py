from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, CourseEmployee
from models.enums import UserRoleEnum


def test_check_course_employee_role_raises_error(db_session):
    """
    Test that associating a CourseEmployee with a user who does not have the employee role raises a DBAPIError.
    Ensures only users with the employee role can be registered for courses.
    """
    not_employee = User(email='not_employee@example.com', hashed_password='hash', is_active=True)
    db_session.add(not_employee)
    db_session.flush()

    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
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


def test_check_course_employee_role_forbidden_for_creator(db_session):
    """
    Test that the course manager cannot register as an employee in their own course.
    Ensures that a user cannot enroll in a course they created.
    """
    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
    db_session.add(employee)

    employee_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(employee_role)

    db_session.flush()

    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    second_manager_role = UserRole(user=manager, role=UserRoleEnum.employee)
    db_session.add(second_manager_role)

    db_session.flush()

    course = Course(title="title", manager_id=manager.id, is_produced=True)
    db_session.add(course)

    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=manager.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "A user cannot register for a course they created!" in str(e.orig)


def test_check_course_employee_role_passes(db_session):
    """
    Test that associating a CourseEmployee with a valid employee user commits successfully.
    Validates role-based restrictions on course enrollment.
    """
    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.flush()

    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title="title", manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
