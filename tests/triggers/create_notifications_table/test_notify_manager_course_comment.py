from models.models import User, UserRole, Course, Content, Task, Comment, Notification
from models.enums import UserRoleEnum


def test_notify_manager_course_comment(db_session):
    """
    Test that a manager receives a notification when a user comments on their course, 
    but does not receive a notification if they comment on their own course.
    """
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id)
    task = Task(question='question', answer='answer')
    db_session.add_all([course, task])

    db_session.flush()

    content = Content(title='title', course_id=course.id, task_id=task.id)
    db_session.add(content)

    db_session.flush()

    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    employee_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(employee_role)

    db_session.flush()

    comment = Comment(text="text", content_id=content.id, user_id=employee.id)
    db_session.add(comment)

    db_session.flush()

    notification = db_session.query(Notification).filter_by(user_id=manager.id).first()
    assert notification is not None
    assert 'Under your course "title", user employee left a comment!' in notification.message

    comment_by_manager = Comment(text="text", content_id=content.id, user_id=manager.id)
    db_session.add(comment_by_manager)

    db_session.flush()

    notification = db_session.query(Notification).filter_by(user_id=manager.id).all()
    assert len(notification) == 1
