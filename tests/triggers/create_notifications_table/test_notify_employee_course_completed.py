from models.models import (
    User, UserRole, Course, Task, Theory, Content,
    CourseEmployee, CourseEmployeeContent, Notification
)
from models.enums import UserRoleEnum, ContentStatusEnum


def test_notify_employee_course_completed_adds_notification(db_session):
    """
    Test that when an employee completes required percent of contents of a course,
    a notification is created for both the employee and the course manager.
    Verifies the functionality of trg_notify_employee_course_completed trigger with passing_percent.
    """
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True, passing_percent=75)
    task = Task(question='question', answer='answer')
    theory = Theory(text='text')
    db_session.add_all([course, task, theory])

    db_session.flush()

    content_task = Content(title='title', course_id=course.id, task_id=task.id)
    content_theory = Content(title='title', course_id=course.id, theory_id=theory.id)
    db_session.add_all([content_task, content_theory])

    db_session.flush()

    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    employee_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(employee_role)

    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    db_session.flush()

    statuses = db_session.query(CourseEmployeeContent).filter_by(course_employee_id=course_employee.id).all()
    assert len(statuses) == 2

    notifications_for_employee_before_change_status = db_session.query(Notification).filter_by(user_id=employee.id).all()
    notifications_for_manager_before_change_status = db_session.query(Notification).filter_by(user_id=manager.id).all()

    statuses[0].status = ContentStatusEnum.done

    db_session.commit()

    notifications_for_employee = db_session.query(Notification).filter_by(user_id=employee.id).all()
    assert len(notifications_for_employee) - len(notifications_for_employee_before_change_status) == 0

    notifications_for_manager = db_session.query(Notification).filter_by(user_id=manager.id).all()
    assert len(notifications_for_manager) - len(notifications_for_manager_before_change_status) == 0

    db_session.refresh(course_employee)
    assert course_employee.is_completed is False

    statuses[1].status = ContentStatusEnum.done

    db_session.commit()

    notifications_for_employee = db_session.query(Notification).filter_by(user_id=employee.id).all()
    assert len(notifications_for_employee) - len(notifications_for_employee_before_change_status) == 1
    assert 'You have successfully completed the "title" course!' in notifications_for_employee[-1].message
    assert notifications_for_employee[-1].is_read is False

    notifications_for_manager = db_session.query(Notification).filter_by(user_id=manager.id).all()
    assert len(notifications_for_manager) - len(notifications_for_manager_before_change_status) == 1
    assert 'The user employee has successfully completed your "title" course.' in notifications_for_manager[-1].message
    assert notifications_for_manager[-1].is_read is False

    db_session.refresh(course_employee)
    assert course_employee.is_completed is True
