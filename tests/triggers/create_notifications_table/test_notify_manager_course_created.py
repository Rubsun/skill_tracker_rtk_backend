from models.models import User, UserRole, Course, Notification
from models.enums import UserRoleEnum


def test_notify_manager_course_produced_adds_notification(db_session):
    """
    Test that when a manager updates a course's is_produced field from False to True,
    a notification is automatically created. Verifies the functionality of
    trg_notify_manager_course_produced trigger.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id)
    db_session.add(course)

    db_session.commit()

    notifications = db_session.query(Notification).filter_by(user_id=manager.id).all()
    assert len(notifications) == 0

    course.is_produced = True

    db_session.commit()

    notifications = db_session.query(Notification).filter_by(user_id=manager.id).all()
    assert len(notifications) == 1
    assert 'You have created and published the "title" course.' in notifications[0].message
    assert notifications[0].is_read is False
