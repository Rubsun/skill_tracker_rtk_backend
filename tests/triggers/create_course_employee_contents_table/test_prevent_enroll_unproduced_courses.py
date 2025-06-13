from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, CourseEmployee
from models.enums import UserRoleEnum


def test_prevent_enroll_unproduced_course(db_session):
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
    db_session.add_all([manager, employee])
    db_session.flush()

    db_session.add_all([
        UserRole(user=manager, role=UserRoleEnum.manager),
        UserRole(user=employee, role=UserRoleEnum.employee),
    ])
    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=False)
    db_session.add(course)
    
    db_session.flush()

    db_session.add(CourseEmployee(course_id=course.id, employee_id=employee.id))

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "Cannot enroll in an unproduced course!" in str(e.orig)
