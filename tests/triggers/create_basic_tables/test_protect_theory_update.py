from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, Content, Theory
from models.enums import UserRoleEnum


def test_protect_theory_update_after_course_produced(db_session):
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    db_session.add(UserRole(user=manager, role=UserRoleEnum.manager))
    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.flush()

    theory = Theory(text='text')
    db_session.add(theory)
    db_session.flush()

    content = Content(title='title', course_id=course.id, theory_id=theory.id)
    db_session.add(content)

    db_session.commit()

    theory.text = 'new text'

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert 'Cannot update theory after course is produced!' in str(e.orig)
