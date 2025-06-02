from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, CourseEmployee
from models.enums import UserRoleEnum


def test_check_course_employee_role_raises_error(db_session):
    not_employee = User(given_name='NotEmployee', family_name='NoRole', username='not_employee', password_hash='hash')
    db_session.add(not_employee)
    db_session.flush()

    user = User(given_name='Иван', family_name='Иванов', username='yes_manager', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.manager)
    db_session.add(user_role)
    db_session.flush()

    course = Course(title="Valid Course", manager_id=user.id)
    db_session.add(course)
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=not_employee.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "Только пользователь с ролью employee может регистрироваться на курсы!" in str(e.orig)


def test_check_course_employee_role_passes(db_session):
    employee = User(given_name='Employee', family_name='Role', username='employee_user', password_hash='hash')
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)
    db_session.flush()

    user = User(given_name='Иван', family_name='Иванов', username='yes_manager', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.manager)
    db_session.add(user_role)
    db_session.flush()

    course = Course(title="Valid Course", manager_id=user.id)
    db_session.add(course)
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
