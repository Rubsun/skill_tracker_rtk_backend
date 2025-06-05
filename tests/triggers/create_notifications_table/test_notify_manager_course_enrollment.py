from models.models import User, Course, CourseEmployee, Notification, UserRole
from models.enums import UserRoleEnum


def test_notify_manager_course_enrollment(db_session):
    """
    Test that a manager receives a notification when a user enrolls in their course.
    """
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    db_session.add(course)

    db_session.flush()

    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    employee_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(employee_role)

    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    db_session.commit()

    notification = db_session.query(Notification).filter_by(user_id=manager.id).first()
    assert notification is not None
    assert 'User employee has signed up for your "title" course!' in notification.message
