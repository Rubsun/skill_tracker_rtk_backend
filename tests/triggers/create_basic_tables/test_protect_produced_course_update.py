from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course
from models.enums import UserRoleEnum


def test_protect_produced_course_update(db_session):
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    db_session.add(UserRole(user=manager, role=UserRoleEnum.manager))
    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.commit()

    course.title = 'new title'

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert 'Only description and deadline can be updated after course is produced!' in str(e.orig)
