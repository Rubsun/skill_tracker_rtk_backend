from models.models import User, UserRole, Course, Notification
from models.enums import UserRoleEnum


def test_notify_course_deletion(db_session):
    """
    Test that when a course is deleted, all enrolled employees receive a notification.
    """
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    manager_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(manager_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    db_session.add(course)

    db_session.flush()

    notifications_before_delete_course = db_session.query(Notification).filter_by(user_id=manager.id).all()

    db_session.delete(course)

    db_session.commit()

    notifications = db_session.query(Notification).filter_by(user_id=manager.id).all()

    assert len(notifications) - len(notifications_before_delete_course) == 1
    assert 'You have deleted your course "title"!' in notifications[-1].message
    assert notifications[0].is_read is False
